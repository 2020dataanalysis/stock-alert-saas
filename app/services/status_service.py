import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path("data/market_data.db")


def get_status_metrics():
    if not DB_PATH.exists():
        return {
            "quote_count": 0,
            "alert_count": 0,
            "streamer_status": "OFFLINE",
            "symbols_tracked": 0,
        }

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM quotes")
    quote_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM alerts")
    alert_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT symbol) FROM quotes")
    symbols_tracked = cursor.fetchone()[0]

    cursor.execute("""
        SELECT timestamp
        FROM quotes
        ORDER BY timestamp DESC
        LIMIT 1
    """)

    result = cursor.fetchone()

    last_quote_time = result[0] if result else None

    if last_quote_time:
        last_dt = datetime.fromisoformat(last_quote_time)
        now = datetime.now(timezone.utc)

        lag_seconds = round(
            (now - last_dt).total_seconds(),
            1
        )
    else:
        lag_seconds = None


    conn.close()

    if lag_seconds is None:
        streamer_status = "OFFLINE"
    elif lag_seconds < 60:
        streamer_status = "ONLINE"
    elif lag_seconds < 300:
        streamer_status = "STALE"
    else:
        streamer_status = "OFFLINE"

    return {
        "quote_count": quote_count,
        "alert_count": alert_count,
        "streamer_status": streamer_status,
        "symbols_tracked": symbols_tracked,
        "lag_seconds": lag_seconds,
    }
