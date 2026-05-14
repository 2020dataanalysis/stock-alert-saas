from app.storage.sqlite_store import get_row_connection


def get_recent_provider_errors(limit=50):

    with get_row_connection() as conn:

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
