from datetime import datetime, timezone
import sqlite3

from app.scalp_state.classifier import classify_scalp_state
from app.scalp_state.database import (
    init_scalp_state_db,
    scalp_state_db_connection,
)
from app.storage.sqlite_store import market_db_connection


DEFAULT_SYMBOLS = [
    "AAPL",
    "MSFT",
    "NVDA",
    "TSLA",
    "WMT",
]


STATE_TRACKER = {}


def get_recent_quotes_for_symbol(symbol, limit=50):

    with market_db_connection() as conn:

        conn.row_factory = sqlite3.Row

        rows = conn.execute("""
            SELECT
                symbol,
                last,
                volume,
                timestamp
            FROM quotes
            WHERE symbol = ?
            ORDER BY id DESC
            LIMIT ?
        """, (symbol, limit)).fetchall()

    quotes = [
        dict(row)
        for row in reversed(rows)
    ]

    return quotes


def classify_transition_type(previous_state, current_state):

    if (
        previous_state == "BUILDING_COMPRESSION"
        and current_state == "ACTIVE_EXPANSION"
    ):
        return "COMPRESSION_BREAKOUT", "HIGH"

    if (
        previous_state == "ACTIVE_EXPANSION"
        and current_state == "AVOID_CHOP"
    ):
        return "MOMENTUM_FAILURE", "MEDIUM"

    if (
        previous_state == "AVOID_CHOP"
        and current_state == "BUILDING_COMPRESSION"
    ):
        return "RANGE_FORMING", "LOW"

    return "STATE_CHANGE", "LOW"


def record_state_transition(classification):

    transition_type, priority = classify_transition_type(
        classification.get("previous_state"),
        classification["state"],
    )

    with scalp_state_db_connection() as conn:

        conn.execute("""
            INSERT INTO scalp_state_transitions (
                timestamp,
                symbol,
                previous_state,
                current_state,
                duration_seconds,
                score,
                range_pct,
                transition_type,
                priority
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now(timezone.utc).isoformat(),
            classification["symbol"],
            classification.get("previous_state"),
            classification["state"],
            classification.get("duration_seconds"),
            classification.get("score"),
            classification.get("range_pct"),
            transition_type,
            priority,
        ))


def enrich_with_state_tracking(classification):

    symbol = classification["symbol"]

    current_state = classification["state"]

    now = datetime.now(timezone.utc)

    previous = STATE_TRACKER.get(symbol)

    if previous is None:

        STATE_TRACKER[symbol] = {
            "state": current_state,
            "entered_at": now,
        }

        classification["previous_state"] = None
        classification["entered_at"] = now.isoformat()
        classification["duration_seconds"] = 0
        classification["state_changed"] = False

        return classification

    previous_state = previous["state"]

    entered_at = previous["entered_at"]

    state_changed = (
        previous_state != current_state
    )

    if state_changed:

        entered_at = now

        STATE_TRACKER[symbol] = {
            "state": current_state,
            "entered_at": entered_at,
        }

    duration_seconds = int(
        (now - entered_at).total_seconds()
    )

    classification["previous_state"] = previous_state
    classification["entered_at"] = entered_at.isoformat()
    classification["duration_seconds"] = duration_seconds
    classification["state_changed"] = state_changed

    if state_changed:
        record_state_transition(classification)

    return classification


def get_scalp_state_rows(symbols=None):

    init_scalp_state_db()

    if symbols is None:
        symbols = DEFAULT_SYMBOLS

    rows = []

    for symbol in symbols:

        recent_quotes = get_recent_quotes_for_symbol(
            symbol=symbol,
            limit=50
        )

        classification = classify_scalp_state(
            symbol=symbol,
            recent_quotes=recent_quotes
        )

        classification = enrich_with_state_tracking(
            classification
        )

        rows.append(classification)

    return rows


def get_recent_state_transitions(limit=25):

    init_scalp_state_db()

    with scalp_state_db_connection() as conn:

        rows = conn.execute("""
            SELECT
                timestamp,
                symbol,
                previous_state,
                current_state,
                duration_seconds,
                score,
                range_pct,
                transition_type,
                priority
            FROM scalp_state_transitions
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

    return [
        dict(row)
        for row in rows
    ]