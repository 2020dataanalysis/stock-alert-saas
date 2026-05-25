from app.storage.sqlite_store import log_db_connection
import sqlite3


def get_recent_provider_errors(limit=50):
    with log_db_connection() as conn:
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
