from app.notifications.gap_alert import (
    build_premarket_gap_event,
    process_premarket_gap_quote,
)


def quote(last=103.0):
    return {
        "symbol": "NVDA",
        "last": last,
        "previous_close": 100.0,
        "open": None,
        "volume": 123456,
        "is_shortable": True,
        "hard_to_borrow": False,
    }


def test_builds_gap_event_at_threshold():
    event = build_premarket_gap_event(
        quote(last=102.0)
    )

    assert event is not None
    assert event.alert_type == "premarket_gap"
    assert event.symbol == "NVDA"
    assert event.details["gap_pct"] == 2.0
    assert event.details["gap_direction"] == "up"


def test_ignores_quote_below_threshold():
    event = build_premarket_gap_event(
        quote(last=101.99)
    )

    assert event is None


def test_duplicate_is_not_dispatched():
    dispatched = []

    class FakeDispatcher:
        def dispatch(self, event):
            dispatched.append(event)
            return {"status": "processed"}

    def existing_event(**kwargs):
        return {
            "id": 1,
            "_created": False,
        }

    result = process_premarket_gap_quote(
        quote(),
        dispatcher=FakeDispatcher(),
        save_event=existing_event,
    )

    assert result["status"] == "duplicate"
    assert dispatched == []


def test_new_gap_is_dispatched():
    dispatched = []

    class FakeDispatcher:
        def dispatch(self, event):
            dispatched.append(event)
            return {"status": "processed"}

    def new_event(**kwargs):
        return {
            "id": 2,
            "_created": True,
        }

    result = process_premarket_gap_quote(
        quote(),
        dispatcher=FakeDispatcher(),
        save_event=new_event,
    )

    assert result["status"] == "dispatched"
    assert len(dispatched) == 1
    assert dispatched[0].symbol == "NVDA"
