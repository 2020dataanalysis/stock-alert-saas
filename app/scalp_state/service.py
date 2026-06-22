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


def get_last_logged_state(symbol):

    with scalp_state_db_connection() as conn:

        row = conn.execute("""
            SELECT
                timestamp,
                state,
                action,
                score,
                range_pct
            FROM scalp_state_log
            WHERE symbol = ?
            ORDER BY id DESC
            LIMIT 1
        """, (symbol,)).fetchone()

    if row is None:
        return None

    return dict(row)


def determine_log_event_type(classification):

    previous_log = get_last_logged_state(
        classification["symbol"]
    )

    if previous_log is None:
        return "SNAPSHOT"

    if previous_log.get("state") != classification.get("state"):
        return "STATE_CHANGE"

    if previous_log.get("action") != classification.get("action"):
        return "ACTION_CHANGE"

    previous_score = previous_log.get("score")
    current_score = classification.get("score")

    if (
        previous_score is not None
        and current_score is not None
        and abs(current_score - previous_score) >= 10
    ):
        return "SCORE_CHANGE"

    previous_range_pct = previous_log.get("range_pct")
    current_range_pct = classification.get("range_pct")

    if (
        previous_range_pct is not None
        and current_range_pct is not None
        and abs(current_range_pct - previous_range_pct) >= 0.10
    ):
        return "RANGE_CHANGE"

    previous_timestamp = previous_log.get("timestamp")

    if previous_timestamp:
        try:
            previous_time = datetime.fromisoformat(previous_timestamp)
            seconds_since_last_log = (
                datetime.now(timezone.utc) - previous_time
            ).total_seconds()

            if seconds_since_last_log >= 15:
                return "TIMED_SNAPSHOT"
        except ValueError:
            return "TIMED_SNAPSHOT"

    return None


def record_scalp_state_log(classification):

    event_type = determine_log_event_type(
        classification
    )

    if event_type is None:
        return

    with scalp_state_db_connection() as conn:

        conn.execute("""
            INSERT INTO scalp_state_log (
                timestamp,
                symbol,
                state,
                previous_state,
                action,
                score,
                latest,
                range_pct,
                range_velocity,
                older_range_pct,
                recent_range_pct,
                directional_efficiency,
                compression_maturity_score,
                compression_label,
                expansion_exhaustion_score,
                expansion_exhaustion_label,
                volume_samples,
                volume_delta,
                volume_delta_per_sample,
                volume_efficiency,
                relative_volume_ratio,
                relative_volume_label,
                reason,
                event_type
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now(timezone.utc).isoformat(),
            classification.get("symbol"),
            classification.get("state"),
            classification.get("previous_state"),
            classification.get("action"),
            classification.get("score"),
            classification.get("latest"),
            classification.get("range_pct"),
            classification.get("range_velocity"),
            classification.get("older_range_pct"),
            classification.get("recent_range_pct"),
            classification.get("directional_efficiency"),
            classification.get("compression_maturity_score"),
            classification.get("compression_label"),
            classification.get("expansion_exhaustion_score"),
            classification.get("expansion_exhaustion_label"),
            classification.get("volume_samples"),
            classification.get("volume_delta"),
            classification.get("volume_delta_per_sample"),
            classification.get("volume_efficiency"),
            classification.get("relative_volume_ratio"),
            classification.get("relative_volume_label"),
            classification.get("reason"),
            event_type,
        ))


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

        record_scalp_state_log(
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

def get_recent_scalp_state_logs(limit=200, symbol=None):

    init_scalp_state_db()

    params = []

    where_clause = ""

    if symbol:
        where_clause = "WHERE symbol = ?"
        params.append(symbol.upper())

    params.append(limit)

    with scalp_state_db_connection() as conn:

        rows = conn.execute(f"""
            SELECT
                timestamp,
                symbol,
                event_type,
                state,
                previous_state,
                action,
                score,
                latest,
                range_pct,
                range_velocity,
                reason
            FROM scalp_state_log
            {where_clause}
            ORDER BY id DESC
            LIMIT ?
        """, params).fetchall()

    return [
        dict(row)
        for row in rows
    ]
