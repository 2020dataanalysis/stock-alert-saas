from datetime import datetime
from zoneinfo import ZoneInfo

from app.storage.sqlite_store import load_market_hours

PACIFIC = ZoneInfo("America/Los_Angeles")


UNKNOWN = "UNKNOWN"
CLOSED = "CLOSED"
PREMARKET = "PREMARKET"
REGULAR = "REGULAR"
AFTER_HOURS = "AFTER_HOURS"


def get_market_windows():
    market_hours = get_schwab_equity_market_hours()

    if not market_hours:
        return {
            "premarket_display": "Unavailable",
            "regular_display": "Unavailable",
            "after_hours_display": "Unavailable",
            "source": "Schwab market hours unavailable",
        }

    session_hours = market_hours.get("sessionHours", {})

    return {
        "premarket_display": format_session_display(
            session_hours.get("preMarket")
        ),
        "regular_display": format_session_display(
            session_hours.get("regularMarket")
        ),
        "after_hours_display": format_session_display(
            session_hours.get("postMarket")
        ),
        "source": "Schwab MarketHours API",
    }


def get_schwab_equity_market_hours():
    market_date = datetime.now(PACIFIC).date().isoformat()

    return load_market_hours(market_date)


def format_session_display(session_list):
    if not session_list:
        return "Closed"

    session = session_list[0]

    start = datetime.fromisoformat(
        session["start"]
    ).astimezone(PACIFIC)

    end = datetime.fromisoformat(
        session["end"]
    ).astimezone(PACIFIC)

    return (
        f"{start.strftime('%-I:%M %p')}"
        f"–{end.strftime('%-I:%M %p')} PT"
    )


def get_market_session():
    market_hours = get_schwab_equity_market_hours()

    if not market_hours:
        return UNKNOWN

    is_open = market_hours.get("isOpen", False)

    if is_open is not True:
        return CLOSED

    now = datetime.now(PACIFIC)
    session_hours = market_hours.get("sessionHours", {})

    if is_now_in_session(now, session_hours.get("preMarket")):
        return PREMARKET

    if is_now_in_session(now, session_hours.get("regularMarket")):
        return REGULAR

    if is_now_in_session(now, session_hours.get("postMarket")):
        return AFTER_HOURS

    return CLOSED


def is_now_in_session(now, session_list):
    if not session_list:
        return False

    for session in session_list:
        start = datetime.fromisoformat(
            session["start"]
        ).astimezone(PACIFIC)

        end = datetime.fromisoformat(
            session["end"]
        ).astimezone(PACIFIC)

        if start <= now < end:
            return True

    return False


def is_regular_market_hours():
    return get_market_session() == REGULAR


def is_trading_session():
    return get_market_session() in {
        PREMARKET,
        REGULAR,
        AFTER_HOURS,
    }


def get_market_is_open():
    session = get_market_session()

    if session == UNKNOWN:
        return None

    return session in {
        PREMARKET,
        REGULAR,
        AFTER_HOURS,
    }


def get_market_status():
    session = get_market_session()
    is_open = get_market_is_open()

    return {
        "market_session": session,
        "market_status": get_market_status_label(session, is_open),
        "is_open": is_open,
        "alerts_enabled": session == REGULAR,
        "market_hours": get_market_windows(),
        "message": get_market_message(session),
    }


def get_market_status_label(session, is_open):
    if session == UNKNOWN:
        return UNKNOWN

    return "OPEN" if is_open else CLOSED


def get_market_message(session):
    if session == REGULAR:
        return "Regular market hours. Alerts are active."

    if session in {PREMARKET, AFTER_HOURS}:
        return (
            "Extended-hours session. Quotes may continue, "
            "but regular alerts are disabled."
        )

    if session == UNKNOWN:
        return (
            "Market hours are unavailable. Treat this as a provider-status "
            "problem, not as confirmed market closed."
        )

    return (
        "Market is closed or today is not a trading day. "
        "Quotes and alerts should be inactive unless manually overridden."
    )
