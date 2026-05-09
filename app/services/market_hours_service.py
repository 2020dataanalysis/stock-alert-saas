from datetime import datetime
from zoneinfo import ZoneInfo

PACIFIC = ZoneInfo("America/Los_Angeles")


def is_regular_market_hours():
    now = datetime.now(PACIFIC)

    # Monday=0, Sunday=6
    if now.weekday() >= 5:
        return False

    market_open = now.replace(hour=6, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=13, minute=0, second=0, microsecond=0)

    return market_open <= now <= market_close


def get_market_status():
    if is_regular_market_hours():
        return {
            "market_status": "OPEN",
            "alerts_enabled": True,
            "message": "Regular market hours. Alerts are active.",
        }

    return {
        "market_status": "CLOSED",
        "alerts_enabled": False,
        "message": "Outside regular market hours. Quotes may continue, but alerts are disabled.",
    }
