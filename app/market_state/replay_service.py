import sqlite3
from pathlib import Path

from app.market_state.storage.event_repository import save_event
from app.market_state.engine.feature_engine import FeatureEngine
from app.market_state.storage.snapshot_repository import save_snapshot
from app.market_state.engine.state_engine import classify_market_state


BASE_DIR = Path(__file__).resolve().parents[2]

MARKET_DATA_DB_PATH = (
    BASE_DIR / "data" / "market_data.db"
)


def replay_quotes(
    symbol,
    date,
    persist_events=True,
    persist_snapshots=True
):

    feature_engine = FeatureEngine()

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
        AND DATE(timestamp) = ?
        ORDER BY timestamp ASC
        """,
        (symbol, date)
    )

    results = []

    for row in cursor.fetchall():

        timestamp, symbol, last, volume = row

        features = feature_engine.update(
            timestamp=timestamp,
            price=last
        )

        classification = classify_market_state(
            features
        )

        state = classification["state"]
        trade_permission = classification["trade_permission"]
        confidence_score = classification["confidence_score"]
        message = classification["message"]

        result = {
            "timestamp": timestamp,
            "symbol": symbol,
            "price": last,
            "volume": volume,
            "features": features,
            "state": state,
            "trade_permission": trade_permission,
            "confidence_score": confidence_score,
            "message": message,
        }

        results.append(result)

        if persist_snapshots:

            save_snapshot(
                timestamp=timestamp,
                symbol=symbol,
                price=last,
                shock_score=features["shock_score"],
                trend_score=features["trend_score"],
                noise_score=features["noise_score"],
                state=state,
                trade_permission=trade_permission
            )

        if persist_events and state != "NORMAL":

            save_event(
                timestamp=timestamp,
                symbol=symbol,
                event_type=state,
                price=last,
                velocity_pct=features["velocity_5s_pct"],
                confidence_score=confidence_score,
                message=message
            )

    market_conn.close()

    return results
