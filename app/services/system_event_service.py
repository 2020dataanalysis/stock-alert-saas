from app.storage.sqlite_store import log_db_connection
import sqlite3


def get_recent_system_events(limit=50):
    with log_db_connection() as conn:
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
