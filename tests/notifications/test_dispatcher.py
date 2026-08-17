from app.notifications.dispatcher import (
    NotificationDispatcher,
)
from app.notifications.event import AlertEvent
from app.notifications.settings import (
    NotificationSettings,
)


def make_settings(
    *,
    enabled_types=frozenset({"premarket_gap"}),
    email_enabled=True,
    ha_webhook_enabled=True,
):
    return NotificationSettings(
        enabled_types=enabled_types,
        email_enabled=email_enabled,
        ha_webhook_enabled=ha_webhook_enabled,
        gmail_username="alerts@example.com",
        gmail_app_password="test-password",
        to_email="sam@example.com",
        ha_webhook_url="http://example.test/webhook",
        request_timeout_seconds=1,
    )


def gap_event():
    return AlertEvent(
        alert_type="premarket_gap",
        symbol="NVDA",
        title="NVDA premarket gap up 3.1%",
        message=(
            "NVDA gap alert. "
            "NVDA is up 3.1 percent."
        ),
        details={"gap_pct": 3.1},
    )


def test_dispatches_gap_to_both_channels():
    sent = []

    def fake_email(event, settings):
        sent.append(("email", event.symbol))
        return {"status_code": 202}

    def fake_ha(event, settings):
        sent.append(
            ("home_assistant", event.symbol)
        )
        return {"status_code": 200}

    dispatcher = NotificationDispatcher(
        settings=make_settings(),
        email_sender=fake_email,
        ha_sender=fake_ha,
    )

    result = dispatcher.dispatch(gap_event())

    assert sent == [
        ("email", "NVDA"),
        ("home_assistant", "NVDA"),
    ]
    assert (
        result["channels"]["email"]["status"]
        == "sent"
    )
    assert (
        result["channels"]["home_assistant"]["status"]
        == "sent"
    )


def test_skips_disabled_alert_type():
    def fail_if_called(event, settings):
        raise AssertionError(
            "Sender should not be called"
        )

    dispatcher = NotificationDispatcher(
        settings=make_settings(),
        email_sender=fail_if_called,
        ha_sender=fail_if_called,
    )

    event = AlertEvent(
        alert_type="price_spike",
        symbol="AAPL",
        title="AAPL price spike",
        message="AAPL moved rapidly.",
    )

    result = dispatcher.dispatch(event)

    assert result["status"] == "skipped"
    assert (
        result["reason"]
        == "alert_type_disabled"
    )


def test_email_failure_does_not_stop_ha():
    def failed_email(event, settings):
        raise RuntimeError("email unavailable")

    def successful_ha(event, settings):
        return {"status_code": 200}

    dispatcher = NotificationDispatcher(
        settings=make_settings(),
        email_sender=failed_email,
        ha_sender=successful_ha,
    )

    result = dispatcher.dispatch(gap_event())

    assert (
        result["channels"]["email"]["status"]
        == "failed"
    )
    assert (
        result["channels"]["home_assistant"]["status"]
        == "sent"
    )
