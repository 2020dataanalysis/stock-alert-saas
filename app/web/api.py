# app/web/api.py

from datetime import datetime, timedelta, timezone
import sqlite3

from fastapi import APIRouter

from app.config import load_settings
from app.storage.sqlite_store import get_connection


router = APIRouter()


@router.post("/api/streamer/mode/{mode}")
def set_mode(mode: str):

    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute("""
        UPDATE streamer_control
        SET mode = ?, until_timestamp = NULL
        WHERE id = 1
        """, (mode,))

        conn.commit()

    return {"status": "ok", "mode": mode}


@router.post("/api/streamer/online-for/{minutes}")
def online_for(minutes: int):

    until = datetime.now(timezone.utc) + timedelta(minutes=minutes)

    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute("""
        UPDATE streamer_control
        SET mode = 'duration', until_timestamp = ?
        WHERE id = 1
        """, (until.isoformat(),))

        conn.commit()

    return {"status": "ok", "until": until.isoformat()}


@router.get("/api/chart-data/{symbol}")
def chart_data(symbol: str):

    settings = load_settings()
    symbol = symbol.upper()

    with get_connection() as conn:

        conn.row_factory = sqlite3.Row

        quotes = conn.execute("""
            SELECT id, timestamp, last, volume
            FROM quotes
            WHERE symbol = ?
            AND timestamp >= datetime('now', '-2 hours')
            ORDER BY id DESC
            LIMIT 200
        """, (symbol,)).fetchall()

        alerts = conn.execute("""
            SELECT timestamp, type, price_change_pct, volume_change_pct
            FROM alerts
            WHERE symbol = ?
            ORDER BY id DESC
            LIMIT 50
        """, (symbol,)).fetchall()

    quotes = list(reversed(quotes))
    alerts = list(reversed(alerts))

    def nearest_quote_index(alert_timestamp):

        alert_dt = datetime.fromisoformat(alert_timestamp)

        best_index = None
        best_delta = None

        for i, q in enumerate(quotes):

            quote_dt = datetime.fromisoformat(q["timestamp"])

            delta = abs(
                (quote_dt - alert_dt).total_seconds()
            )

            if best_delta is None or delta < best_delta:
                best_delta = delta
                best_index = i

        if best_delta is not None and best_delta <= 30:
            return best_index

        return None

    chart_alerts = []

    for alert in alerts:

        index = nearest_quote_index(alert["timestamp"])

        if index is None:
            continue

        chart_alerts.append({
            "index": index,
            "timestamp": alert["timestamp"],
            "type": alert["type"],
            "price_change_pct": alert["price_change_pct"],
            "volume_change_pct": alert["volume_change_pct"],
        })

    return {
        "symbol": symbol,
        "settings": {
            "price_spike_pct": settings["price_spike_pct"],
            "volume_spike_pct": settings["volume_spike_pct"],
        },
        "timestamps": [q["timestamp"] for q in quotes],
        "prices": [q["last"] for q in quotes],
        "volumes": [q["volume"] for q in quotes],
        "alerts": chart_alerts,
    }