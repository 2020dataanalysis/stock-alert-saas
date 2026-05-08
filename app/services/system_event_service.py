import sqlite3
from pathlib import Path

DB_PATH = Path("data/market_data.db")


def get_recent_system_events(limit=50):
    if not DB_PATH.exists():
        return []

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        cursor = conn.execute("""
            SELECT
                timestamp,
                event_type,
                service,
                status,
                message,
                metadata_json
            FROM system_events
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))

        return cursor.fetchall()
