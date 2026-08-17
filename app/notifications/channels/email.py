from __future__ import annotations

import smtplib
from email.message import EmailMessage

from app.notifications.event import AlertEvent
from app.notifications.settings import (
    NotificationSettings,
)


def send_email(
    event: AlertEvent,
    settings: NotificationSettings,
) -> dict:
    missing = [
        name
        for name, value in (
            (
                "GMAIL_SMTP_USERNAME",
                settings.gmail_username,
            ),
            (
                "GMAIL_SMTP_APP_PASSWORD",
                settings.gmail_app_password,
            ),
            (
                "ALERT_TO_EMAIL",
                settings.to_email,
            ),
        )
        if not value
    ]

    if missing:
        raise RuntimeError(
            "Missing Gmail configuration: "
            + ", ".join(missing)
        )

    message = EmailMessage()
    message["From"] = settings.gmail_username
    message["To"] = settings.to_email
    message["Subject"] = event.title
    message.set_content(event.message)

    try:
        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465,
            timeout=settings.request_timeout_seconds,
        ) as smtp:
            smtp.login(
                settings.gmail_username,
                settings.gmail_app_password,
            )
            smtp.send_message(message)
    except (smtplib.SMTPException, OSError) as exc:
        raise RuntimeError(
            "Gmail SMTP request failed "
            f"({type(exc).__name__})"
        ) from exc

    return {"status_code": 250}
