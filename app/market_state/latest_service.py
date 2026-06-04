"""
|--------------------------------------------------------------------------
| File: latest_service.py
|--------------------------------------------------------------------------
| Latest market-state calculation from recent quote history.
|--------------------------------------------------------------------------
"""

import sqlite3
from pathlib import Path

from app.market_state.event_log_service import (
    append_high_noise_event,
    append_market_event,
    append_permission_blocked_event,
    append_shock_threshold_event,
)
from app.market_state.engine.feature_engine import FeatureEngine
from app.market_state.engine.state_engine import classify_market_state


BASE_DIR = Path(__file__).resolve().parents[2]

MARKET_DATA_DB_PATH = (
    BASE_DIR / "data" / "market_data.db"
)

LAST_STATE_BY_SYMBOL = {}
LAST_PERMISSION_BY_SYMBOL = {}
LAST_THRESHOLD_FLAGS_BY_SYMBOL = {}


def get_latest_market_state(
    symbol,
    limit=200
):

    market_conn = sqlite3.connect(
        MARKET_DATA_DB_PATH
    )

    cursor = market_conn.execute(
        """
        SELECT
            timestamp,
            symbol,
            last,
            volume
        FROM quotes
        WHERE symbol = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (
            symbol,
            limit
        )
    )

    rows = cursor.fetchall()

    market_conn.close()

    rows.reverse()

    feature_engine = FeatureEngine()

    latest_result = None

    for row in rows:

        timestamp, symbol, last, volume = row

        features = feature_engine.update(
            timestamp=timestamp,
            price=last
        )

        classification = classify_market_state(
            features
        )

        latest_result = {
            "timestamp": timestamp,
            "symbol": symbol,
            "price": last,
            "volume": volume,
            "features": features,
            "state": classification["state"],
            "trade_permission": classification[
                "trade_permission"
            ],
            "confidence_score": classification[
                "confidence_score"
            ],
            "message": classification["message"],
        }

    if latest_result is None:

        return {
            "symbol": symbol,
            "state": "NO_DATA",
            "trade_permission": "WAIT",
            "message": "No quotes found for symbol",
        }

    record_state_transition(
        latest_result
    )

    record_permission_transition(
        latest_result
    )

    record_threshold_events(
        latest_result
    )

    return latest_result


def record_state_transition(result):

    symbol = result["symbol"]
    current_state = result["state"]

    previous_state = LAST_STATE_BY_SYMBOL.get(
        symbol
    )

    if previous_state is None:

        LAST_STATE_BY_SYMBOL[symbol] = current_state

        append_market_event(
            event_type="STATE_INITIALIZED",
            message=(
                f"{symbol} initialized "
                f"state={current_state}"
            ),
            metadata=result
        )

        return

    if previous_state == current_state:
        return

    LAST_STATE_BY_SYMBOL[symbol] = current_state

    append_market_event(
        event_type="STATE_TRANSITION",
        message=(
            f"{symbol} {previous_state} "
            f"-> {current_state}"
        ),
        metadata=result
    )


def record_permission_transition(result):

    symbol = result["symbol"]
    current_permission = result["trade_permission"]

    previous_permission = (
        LAST_PERMISSION_BY_SYMBOL.get(symbol)
    )

    if previous_permission is None:

        LAST_PERMISSION_BY_SYMBOL[symbol] = (
            current_permission
        )

        return

    if previous_permission == current_permission:
        return

    LAST_PERMISSION_BY_SYMBOL[symbol] = (
        current_permission
    )

    append_market_event(
        event_type="PERMISSION_TRANSITION",
        message=(
            f"{symbol} {previous_permission} "
            f"-> {current_permission}"
        ),
        metadata=result
    )

    if current_permission == "BLOCK":

        append_permission_blocked_event(
            result
        )


def record_threshold_events(result):

    symbol = result["symbol"]

    flags = LAST_THRESHOLD_FLAGS_BY_SYMBOL.setdefault(
        symbol,
        {
            "shock_threshold": False,
            "high_noise": False,
        }
    )

    shock_score = result["features"]["shock_score"]
    noise_score = result["features"]["noise_score"]

    shock_triggered = shock_score >= 1.5
    high_noise_triggered = noise_score >= 2.0

    if shock_triggered and not flags["shock_threshold"]:

        append_shock_threshold_event(
            result
        )

    if high_noise_triggered and not flags["high_noise"]:

        append_high_noise_event(
            result
        )

    flags["shock_threshold"] = shock_triggered
    flags["high_noise"] = high_noise_triggered
