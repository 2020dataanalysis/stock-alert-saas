from app.storage.sqlite_store import get_row_connection


def get_replay_quotes(
    symbol,
    trade_date=None,
    limit=10000,
):
    with get_row_connection() as conn:

        sql = """
            SELECT
                timestamp,
                last,
                volume
            FROM quotes
            WHERE symbol = ?
        """

        params = [symbol.upper()]

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

        return [
            {
                "timestamp": row["timestamp"],
                "last": row["last"],
                "volume": row["volume"],
            }
            for row in rows
        ]
