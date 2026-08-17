from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


def _enabled(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _enabled_types() -> frozenset[str]:
    value = os.getenv(
        "ALERT_ENABLED_TYPES",
        "premarket_gap",
    )

    return frozenset(
        item.strip().lower()
        for item in value.split(",")
        if item.strip()
    )


@dataclass(frozen=True, slots=True)
class NotificationSettings:
    enabled_types: frozenset[str]
    email_enabled: bool
    ha_webhook_enabled: bool
    gmail_username: str | None
    gmail_app_password: str | None
    to_email: str | None
    ha_webhook_url: str | None
    request_timeout_seconds: float


def load_notification_settings() -> NotificationSettings:
    return NotificationSettings(
        enabled_types=_enabled_types(),
        email_enabled=_enabled("ALERT_EMAIL_ENABLED"),
        ha_webhook_enabled=_enabled(
            "ALERT_HA_TTS_ENABLED"
        ),
        gmail_username=os.getenv(
            "GMAIL_SMTP_USERNAME"
        ),
        gmail_app_password=os.getenv(
            "GMAIL_SMTP_APP_PASSWORD"
        ),
        to_email=os.getenv("ALERT_TO_EMAIL"),
        ha_webhook_url=os.getenv(
            "HA_ALERT_WEBHOOK_URL"
        ),
        request_timeout_seconds=float(
            os.getenv(
                "ALERT_REQUEST_TIMEOUT_SECONDS",
                "5",
            )
        ),
    )
