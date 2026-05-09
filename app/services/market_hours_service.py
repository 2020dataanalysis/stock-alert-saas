from datetime import datetime
from zoneinfo import ZoneInfo

PACIFIC = ZoneInfo("America/Los_Angeles")


def get_market_session():
    now = datetime.now(PACIFIC)

    # Monday=0, Sunday=6
    if now.weekday() >= 5:
        return "CLOSED"

    premarket_start = now.replace(hour=4, minute=0, second=0, microsecond=0)
    regular_start = now.replace(hour=6, minute=30, second=0, microsecond=0)
    regular_end = now.replace(hour=13, minute=0, second=0, microsecond=0)
    after_hours_end = now.replace(hour=17, minute=0, second=0, microsecond=0)

    if premarket_start <= now < regular_start:
        return "PREMARKET"

    if regular_start <= now < regular_end:
        return "REGULAR"

    if regular_end <= now < after_hours_end:
        return "AFTER_HOURS"

    return "CLOSED"


def is_regular_market_hours():
    return get_market_session() == "REGULAR"


def is_trading_session():
    return get_market_session() in {
        "PREMARKET",
        "REGULAR",
        "AFTER_HOURS",
    }


def get_market_status():
    session = get_market_session()

    return {
        "market_session": session,
        "market_status": "OPEN" if session != "CLOSED" else "CLOSED",
        "alerts_enabled": session == "REGULAR",
        "message": (
            "Regular market hours. Alerts are active."
            if session == "REGULAR"
            else "Extended-hours session. Quotes may continue, but regular alerts are disabled."
            if session in {"PREMARKET", "AFTER_HOURS"}
            else "Market is closed. Quotes and alerts should be inactive unless manually overridden."
        ),
    }
