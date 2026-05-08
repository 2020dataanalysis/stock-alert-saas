import sqlite3
from pathlib import Path

DB_PATH = Path("data/market_data.db")


def get_recent_alerts(limit=50):
    if not DB_PATH.exists():
        return []

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        cursor = conn.execute("""
            SELECT
                symbol,
                type,
                price_change_pct,
                volume_change_pct,
                oldest_price,
                newest_price,
                oldest_volume,
                newest_volume,
                timestamp
            FROM alerts
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))

        return cursor.fetchall()
