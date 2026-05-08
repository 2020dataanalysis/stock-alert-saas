import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path("data/market_data.db")


def get_streamer_mode():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT mode, until_timestamp FROM streamer_control WHERE id = 1")
    row = cur.fetchone()
    conn.close()

    if not row:
        return "auto"

    mode, until_ts = row

    if mode == "duration" and until_ts:
        now = datetime.now(timezone.utc)
        until = datetime.fromisoformat(until_ts)

        if now > until:
            return "auto"
        return "online"

    return mode



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
