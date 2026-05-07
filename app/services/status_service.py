import sqlite3
from pathlib import Path


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

    conn.close()

    return {
        "quote_count": quote_count,
        "alert_count": alert_count,
        "streamer_status": "ONLINE" if quote_count > 0 else "OFFLINE",
        "symbols_tracked": symbols_tracked,
    }