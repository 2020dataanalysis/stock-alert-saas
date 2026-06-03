from datetime import datetime

from app.storage.sqlite_store import get_row_connection


def _date_part(timestamp):
    if not timestamp:
        return None

    return timestamp[:10]


def _time_part(timestamp):
    if not timestamp:
        return None

    return timestamp[11:19]


def _format_duration(start_timestamp, end_timestamp):
    if not start_timestamp or not end_timestamp:
        return None

    start = datetime.fromisoformat(start_timestamp)
    end = datetime.fromisoformat(end_timestamp)

    seconds = int((end - start).total_seconds())

    days = seconds // 86400
    seconds %= 86400

    hours = seconds // 3600
    seconds %= 3600

    minutes = seconds // 60

    parts = []

    if days:
        parts.append(f"{days}d")

    if hours:
        parts.append(f"{hours}h")

    if minutes:
        parts.append(f"{minutes}m")

    if not parts:
        return "0m"

    return " ".join(parts)


def get_replay_summary(symbol):
    normalized_symbol = symbol.upper()

    with get_row_connection() as conn:
        row = conn.execute("""
            SELECT
                symbol,
                MIN(timestamp) AS first_quote_at,
                MAX(timestamp) AS last_quote_at,
                COUNT(*) AS data_points
            FROM quotes
            WHERE symbol = ?
            GROUP BY symbol
        """, (normalized_symbol,)).fetchone()

        if not row:
            return {
                "symbol": normalized_symbol,
                "found": False,
                "message": "No replay data found for symbol.",
            }

        item = dict(row)

        start_timestamp = item["first_quote_at"]
        end_timestamp = item["last_quote_at"]

        return {
            "symbol": item["symbol"],
            "found": True,
            "start_date": _date_part(start_timestamp),
            "end_date": _date_part(end_timestamp),
            "start_time": _time_part(start_timestamp),
            "end_time": _time_part(end_timestamp),
            "duration": _format_duration(
                start_timestamp,
                end_timestamp,
            ),
            "data_points": item["data_points"],
        }
