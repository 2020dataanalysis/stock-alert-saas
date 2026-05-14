from app.storage.sqlite_store import get_row_connection

def get_recent_system_events(limit=50):
    with get_row_connection() as conn:

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
