import sqlite3
from pathlib import Path


DB_PATH = Path("data/market_data.db")


def get_recent_quotes(symbol="AAPL", limit=100):
    if not DB_PATH.exists():
        return []

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
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

    conn.close()

    rows = list(reversed(rows))

    return [
        {
            "timestamp": row["timestamp"],
            "price": row["last"],
        }
        for row in rows
    ]
