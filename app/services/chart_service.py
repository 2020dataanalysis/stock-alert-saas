from app.storage.sqlite_store import get_row_connection


def get_recent_quotes(symbol="AAPL", limit=100):
    with get_row_connection() as conn:

        cursor = conn.execute(
            """
            SELECT timestamp, last
            FROM quotes
            WHERE symbol = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (symbol, limit),
        )

        rows = cursor.fetchall()

    rows = list(reversed(rows))

    return [
        {
            "timestamp": row["timestamp"],
            "price": row["last"],
        }
        for row in rows
    ]