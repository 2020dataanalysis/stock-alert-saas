from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from app.gappers.storage import save_gap_event
from app.notifications.dispatcher import (
    NotificationDispatcher,
)
from app.notifications.event import AlertEvent


PACIFIC = ZoneInfo("America/Los_Angeles")


def calculate_gap_pct(
    current_price: float | None,
    previous_close: float | None,
) -> float | None:
    if current_price is None:
        return None

    if previous_close in (None, 0):
        return None

    return (
        (current_price - previous_close)
        * 100.0
        / previous_close
    )


def build_premarket_gap_event(
    quote: dict[str, Any],
    minimum_gap_pct: float = 2.0,
) -> AlertEvent | None:
    symbol = str(quote.get("symbol", "")).upper()
    current_price = quote.get("last")
    previous_close = quote.get("previous_close")

    gap_pct = calculate_gap_pct(
        current_price,
        previous_close,
    )

    if not symbol or gap_pct is None:
        return None

    if abs(gap_pct) < minimum_gap_pct:
        return None

    direction = "up" if gap_pct > 0 else "down"
    magnitude = abs(gap_pct)

    return AlertEvent(
        alert_type="premarket_gap",
        symbol=symbol,
        title=(
            f"{symbol} premarket gap "
            f"{direction} {magnitude:.2f}%"
        ),
        message=(
            f"{symbol} gap alert. "
            f"{symbol} is {direction} "
            f"{magnitude:.2f} percent "
            f"in premarket trading."
        ),
        details={
            "gap_pct": round(gap_pct, 4),
            "gap_direction": direction,
            "previous_close": previous_close,
            "current_price": current_price,
            "open_price": quote.get("open"),
            "volume": quote.get("volume"),
        },
    )


def process_premarket_gap_quote(
    quote: dict[str, Any],
    *,
    minimum_gap_pct: float = 2.0,
    dispatcher: NotificationDispatcher | None = None,
    save_event: Callable[..., dict] = save_gap_event,
) -> dict[str, Any]:
    event = build_premarket_gap_event(
        quote,
        minimum_gap_pct=minimum_gap_pct,
    )

    if event is None:
        return {"status": "not_qualified"}

    now = datetime.now(PACIFIC)
    details = event.details

    saved = save_event(
        symbol=event.symbol,
        trade_date=now.date().isoformat(),
        detected_at=event.occurred_at,
        gap_pct=details["gap_pct"],
        gap_direction=details["gap_direction"],
        previous_close=details["previous_close"],
        open_price=details["open_price"],
        last_price=details["current_price"],
        volume=details["volume"],
        is_shortable=quote.get("is_shortable"),
        hard_to_borrow=quote.get("hard_to_borrow"),
        source="quote_streamer",
    )

    if not saved.get("_created", False):
        return {
            "status": "duplicate",
            "event": event,
            "saved": saved,
        }

    active_dispatcher = (
        dispatcher or NotificationDispatcher()
    )

    return {
        "status": "dispatched",
        "event": event,
        "saved": saved,
        "notification": active_dispatcher.dispatch(event),
    }
