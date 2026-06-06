from app.storage.sqlite_store import get_row_connection
from app.historical_data.replay.alert_simulation_service import (
    simulate_replay_alerts,
)


def get_replay_quotes(
    symbol,
    trade_date=None,
    limit=10000,
):
    requested_symbol = symbol.upper()

    with get_row_connection() as conn:

        sql = """
            SELECT
                symbol,
                timestamp,
                last,
                volume
            FROM quotes
            WHERE symbol = ?
        """

        params = [requested_symbol]

        if trade_date:
            sql += """
                AND substr(timestamp, 1, 10) = ?
            """
            params.append(trade_date)

        sql += """
            ORDER BY timestamp ASC
            LIMIT ?
        """

        params.append(limit)

        rows = conn.execute(
            sql,
            params,
        ).fetchall()

        quotes = [
            {
                "symbol": row["symbol"],
                "timestamp": row["timestamp"],
                "last": row["last"],
                "volume": row["volume"],
            }
            for row in rows
        ]

    return {
        "quotes": quotes,
        "simulated_alerts": simulate_replay_alerts(quotes),
    }
