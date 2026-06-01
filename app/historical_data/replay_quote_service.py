from app.storage.sqlite_store import get_row_connection


def get_replay_quotes(
    symbol,
    limit=10000,
):
    with get_row_connection() as conn:

        rows = conn.execute("""
            SELECT
                timestamp,
                last,
                volume
            FROM quotes
            WHERE symbol = ?
            ORDER BY timestamp ASC
            LIMIT ?
        """, (
            symbol.upper(),
            limit,
        )).fetchall()

        return [
            {
                "timestamp": row["timestamp"],
                "last": row["last"],
                "volume": row["volume"],
            }
            for row in rows
        ]
