"""
|--------------------------------------------------------------------------
| File: event_log_service.py
|--------------------------------------------------------------------------
| Market-state transition and threshold event persistence.
|--------------------------------------------------------------------------
"""

from collections import deque


EVENT_LOG = deque(maxlen=500)


def append_market_event(
    event_type,
    message,
    metadata=None
):

    EVENT_LOG.appendleft({
        "event_type": event_type,
        "message": message,
        "metadata": metadata or {},
    })


def append_shock_threshold_event(result):

    append_market_event(
        event_type="SHOCK_THRESHOLD_EXCEEDED",
        message=(
            f"{result['symbol']} shock_score="
            f"{result['features']['shock_score']:.2f}"
        ),
        metadata=result
    )


def append_high_noise_event(result):

    append_market_event(
        event_type="HIGH_NOISE",
        message=(
            f"{result['symbol']} noise_score="
            f"{result['features']['noise_score']:.2f}"
        ),
        metadata=result
    )


def append_permission_blocked_event(result):

    append_market_event(
        event_type="PERMISSION_BLOCKED",
        message=(
            f"{result['symbol']} trade_permission=BLOCK"
        ),
        metadata=result
    )


def get_recent_market_events(limit=100):

    return list(EVENT_LOG)[:limit]
