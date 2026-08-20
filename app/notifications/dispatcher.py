from __future__ import annotations

from collections.abc import Callable

from app.notifications.channels.email import send_email
from app.notifications.channels.home_assistant import (
    send_home_assistant_webhook,
)
from app.notifications.event import AlertEvent
from app.notifications.settings import (
    NotificationSettings,
    load_notification_settings,
)

Sender = Callable[
    [AlertEvent, NotificationSettings],
    dict,
]


class NotificationDispatcher:
    def __init__(
        self,
        settings: NotificationSettings | None = None,
        email_sender: Sender = send_email,
        ha_sender: Sender = send_home_assistant_webhook,
    ):
        self.settings = (
            settings or load_notification_settings()
        )
        self.email_sender = email_sender
        self.ha_sender = ha_sender

    def dispatch(self, event: AlertEvent) -> dict:
        alert_type = event.alert_type.lower()

        email_types = (
            self.settings.email_enabled_types
            or self.settings.enabled_types
        )
        ha_types = (
            self.settings.ha_enabled_types
            or self.settings.enabled_types
        )

        send_email_for_type = (
            self.settings.email_enabled
            and alert_type in email_types
        )
        send_ha_for_type = (
            self.settings.ha_webhook_enabled
            and alert_type in ha_types
        )

        if not send_email_for_type and not send_ha_for_type:
            return {
                "alert_type": alert_type,
                "status": "skipped",
                "reason": "alert_type_disabled",
                "channels": {},
            }

        results: dict[str, dict] = {}

        if send_email_for_type:
            results["email"] = self._attempt(
                self.email_sender,
                event,
            )

        if send_ha_for_type:
            results["home_assistant"] = self._attempt(
                self.ha_sender,
                event,
            )

        return {
            "alert_type": alert_type,
            "status": "processed",
            "channels": results,
        }

    def _attempt(
        self,
        sender: Sender,
        event: AlertEvent,
    ) -> dict:
        try:
            return {
                "status": "sent",
                **sender(event, self.settings),
            }
        except Exception as exc:
            return {
                "status": "failed",
                "error": (
                    f"{type(exc).__name__}: {exc}"
                ),
            }
