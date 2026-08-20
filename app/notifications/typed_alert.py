from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.notifications.dispatcher import NotificationDispatcher
from app.notifications.event import AlertEvent


SUPPORTED_TYPES = frozenset(
    {"threshold", "whale_spike", "whale_drop"}
)


def _number(value: Any, digits: int = 2) -> str:
    return f"{float(value):.{digits}f}"


def build_typed_alert_event(alert: dict) -> AlertEvent | None:
    alert_type = str(alert.get("type", "")).lower()

    if alert_type not in SUPPORTED_TYPES:
        return None

    symbol = str(alert["symbol"]).upper()

    if alert_type in {"whale_spike", "whale_drop"}:
        direction = (
            "up" if alert_type == "whale_spike" else "down"
        )
        verb = "rose" if direction == "up" else "fell"
        price_change = abs(
            float(alert["price_change_pct"])
        )
        volume_change = float(
            alert["volume_change_pct"]
        )

        title = f"{symbol} whale move {direction}"
        message = (
            f"{symbol} whale move {direction}. "
            f"Price {verb} {_number(price_change)} percent, "
            f"from {_number(alert['oldest_price'])} to "
            f"{_number(alert['newest_price'])}. "
            f"Volume increased "
            f"{_number(volume_change, 1)} percent."
        )
    else:
        title = f"{symbol} price alert"
        message = f"{symbol} price alert triggered."

    details = {
        key: value
        for key, value in alert.items()
        if key
        not in {
            "type",
            "symbol",
            "message",
            "timestamp",
        }
    }

    return AlertEvent(
        alert_type=alert_type,
        symbol=symbol,
        title=title,
        message=message,
        occurred_at=(
            alert.get("timestamp")
            or datetime.now(timezone.utc).isoformat()
        ),
        details=details,
    )


def dispatch_typed_alert(
    alert: dict,
    dispatcher: NotificationDispatcher | None = None,
) -> dict:
    event = build_typed_alert_event(alert)

    if event is None:
        return {
            "status": "skipped",
            "reason": "unsupported_alert_type",
        }

    active_dispatcher = (
        dispatcher or NotificationDispatcher()
    )

    return active_dispatcher.dispatch(event)
