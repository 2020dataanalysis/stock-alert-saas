import sqlite3
from pathlib import Path

DB_PATH = Path("data/market_data.db")


def get_recent_provider_errors(limit=50):
    if not DB_PATH.exists():
        return []

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        cursor = conn.execute("""
            SELECT
                timestamp,
                provider,
                symbol,
                operation,
                error_type,
                message,
                raw_response
            FROM provider_errors
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))

        return cursor.fetchall()
