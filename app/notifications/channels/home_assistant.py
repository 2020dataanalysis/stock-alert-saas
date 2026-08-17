from __future__ import annotations

import requests

from app.notifications.event import AlertEvent
from app.notifications.settings import NotificationSettings


def send_home_assistant_webhook(
    event: AlertEvent,
    settings: NotificationSettings,
) -> dict:
    if not settings.ha_webhook_url:
        raise RuntimeError(
            "Missing Home Assistant configuration: "
            "HA_ALERT_WEBHOOK_URL"
        )

    try:
        response = requests.post(
            settings.ha_webhook_url,
            json=event.as_payload(),
            timeout=settings.request_timeout_seconds,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(
            "Home Assistant webhook request failed "
            f"({type(exc).__name__})"
        ) from exc

    return {"status_code": response.status_code}
