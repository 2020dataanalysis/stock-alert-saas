from app.storage.sqlite_store import get_row_connection


def get_recent_alerts(limit=50):
    with get_row_connection() as conn:

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
