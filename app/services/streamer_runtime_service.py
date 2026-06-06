from app.services.status_service import get_streamer_mode
from app.services.market_hours_service import (
    CLOSED,
    REGULAR,
    PREMARKET,
    AFTER_HOURS,
    get_market_session,
)


def get_sleep_seconds(mode, session, poll_seconds):
    if mode == "offline":
        return 5

    if session == CLOSED:
        return 5

    if session in {PREMARKET, AFTER_HOURS}:
        return max(poll_seconds, 30)

    return poll_seconds


def get_runtime_state(poll_seconds):
    mode = get_streamer_mode()
    session = get_market_session()

    should_fetch_quotes = (
        mode != "offline"
        and session in {REGULAR, PREMARKET, AFTER_HOURS}
    )

    should_process_alerts = (
        should_fetch_quotes
        and session == REGULAR
    )

    return {
        "mode": mode,
        "session": session,
        "should_fetch_quotes": should_fetch_quotes,
        "should_process_alerts": should_process_alerts,
        "sleep_seconds": get_sleep_seconds(mode, session, poll_seconds),
    }
