from app.storage.sqlite_store import get_row_connection


def get_replay_dates(symbol):
    with get_row_connection() as conn:

        rows = conn.execute("""
            SELECT
                substr(timestamp, 1, 10) AS trade_date,
                COUNT(*) AS quote_count,
                MIN(timestamp) AS first_quote,
                MAX(timestamp) AS last_quote
            FROM quotes
            WHERE symbol = ?
            GROUP BY substr(timestamp, 1, 10)
            ORDER BY trade_date
        """, (
            symbol.upper(),
        )).fetchall()

        return [
            {
                "trade_date": row["trade_date"],
                "quote_count": row["quote_count"],
                "first_quote": row["first_quote"],
                "last_quote": row["last_quote"],
            }
            for row in rows
        ]
