"""
|--------------------------------------------------------------------------
| File: event_log_service.py
|--------------------------------------------------------------------------
| Market-state transition and telemetry event persistence.
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


def get_recent_market_events(limit=100):

    return list(EVENT_LOG)[:limit]
