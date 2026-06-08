from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.config import load_settings
from app.data_adapters.movers_adapter import get_mover_symbols
from app.data_adapters.schwab_adapter import SchwabAdapter
from app.gappers.db_init import initialize_gap_database
from app.gappers.storage import save_gap_event


def _calculate_gap_pct(open_price: float | None, previous_close: float | None) -> float | None:
    if open_price is None or previous_close in (None, 0):
        return None

    return (open_price - previous_close) * 100.0 / previous_close



def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _today_utc_date() -> str:
    return datetime.now(timezone.utc).date().isoformat()

def get_live_gappers(
    minimum_gap_pct: float = 2.0,
    limit: int | None = None,
) -> dict[str, Any]:
    initialize_gap_database()

    settings = load_settings()
    movers_limit = limit or settings.get("movers_limit", 10)

    mover_symbols = get_mover_symbols(limit=movers_limit)
    adapter = SchwabAdapter()

    detected_at = _utc_now_iso()
    trade_date = _today_utc_date()

    rows: list[dict[str, Any]] = []

    for symbol in mover_symbols:
        quote = adapter.get_quote(symbol)

        if not quote:
            continue

        gap_pct = _calculate_gap_pct(
            quote.get("open"),
            quote.get("previous_close"),
        )

        if gap_pct is None:
            continue

        if abs(gap_pct) < minimum_gap_pct:
            continue

        direction = "up" if gap_pct > 0 else "down"

        saved_event = save_gap_event(
            symbol=symbol,
            trade_date=trade_date,
            detected_at=detected_at,
            gap_pct=round(gap_pct, 4),
            gap_direction=direction,
            previous_close=quote.get("previous_close"),
            open_price=quote.get("open"),
            last_price=quote.get("last"),
            volume=quote.get("volume"),
            is_shortable=quote.get("is_shortable"),
            hard_to_borrow=quote.get("hard_to_borrow"),
            source="movers",
        )

        rows.append(
            {
                "symbol": symbol,
                "trade_date": trade_date,
                "gap_event_id": saved_event.get("id"),
                "gap_pct": round(gap_pct, 4),
                "direction": direction,
                "previous_close": quote.get("previous_close"),
                "open": quote.get("open"),
                "last": quote.get("last"),
                "net_percent_change": quote.get("net_percent_change"),
                "volume": quote.get("volume"),
                "is_shortable": quote.get("is_shortable"),
                "hard_to_borrow": quote.get("hard_to_borrow"),
            }
        )

    rows.sort(
        key=lambda row: abs(row["gap_pct"]),
        reverse=True,
    )

    return {
        "minimum_gap_pct": minimum_gap_pct,
        "source": "movers",
        "mover_count": len(mover_symbols),
        "gapper_count": len(rows),
        "gappers": rows,
    }


def get_gap_event_detail(
    symbol: str,
    trade_date: str,
    minimum_gap_pct: float = 2.0,
    research_lookback_days: int | None = 365,
):
    from app.gappers.storage import (
        get_gap_event,
        get_gap_outcome,
        count_prior_gap_events,
        count_prior_gap_events_by_direction,
    )

    event = get_gap_event(
        symbol=symbol,
        trade_date=trade_date,
    )

    if not event:
        return {
            "found": False,
        }

    outcome = get_gap_outcome(
        event["id"]
    )

    return {
        "found": True,
        "event": event,
        "outcome": outcome,
        "historical_sample": {
            "minimum_gap_pct": minimum_gap_pct,
            "research_lookback_days": research_lookback_days,
            "total": count_prior_gap_events(
                symbol=symbol,
                trade_date=trade_date,
                minimum_gap_pct=minimum_gap_pct,
                lookback_days=research_lookback_days,
            ),
            "directions": count_prior_gap_events_by_direction(
                symbol=symbol,
                trade_date=trade_date,
                minimum_gap_pct=minimum_gap_pct,
                lookback_days=research_lookback_days,
            ),
        },
    }


def get_gap_event_detail(
    symbol: str,
    trade_date: str,
    minimum_gap_pct: float = 2.0,
    research_lookback_days: int | None = 365,
):
    from app.gappers.storage import (
        get_gap_event,
        get_gap_outcome,
        count_prior_gap_events,
        count_prior_gap_events_by_direction,
    )

    event = get_gap_event(
        symbol=symbol,
        trade_date=trade_date,
    )

    if not event:
        return {
            "found": False,
        }

    outcome = get_gap_outcome(
        event["id"]
    )

    return {
        "found": True,
        "event": event,
        "outcome": outcome,
        "historical_sample": {
            "minimum_gap_pct": minimum_gap_pct,
            "research_lookback_days": research_lookback_days,
            "total": count_prior_gap_events(
                symbol=symbol,
                trade_date=trade_date,
                minimum_gap_pct=minimum_gap_pct,
                lookback_days=research_lookback_days,
            ),
            "directions": count_prior_gap_events_by_direction(
                symbol=symbol,
                trade_date=trade_date,
                minimum_gap_pct=minimum_gap_pct,
                lookback_days=research_lookback_days,
            ),
        },
    }


def get_gap_event_detail(
    symbol: str,
    trade_date: str,
    minimum_gap_pct: float = 2.0,
    research_lookback_days: int | None = 365,
):
    from app.gappers.storage import (
        get_gap_event,
        get_gap_outcome,
        count_prior_gap_events,
        count_prior_gap_events_by_direction,
    )

    event = get_gap_event(
        symbol=symbol,
        trade_date=trade_date,
    )

    if not event:
        return {
            "found": False,
        }

    outcome = get_gap_outcome(
        event["id"]
    )

    return {
        "found": True,
        "event": event,
        "outcome": outcome,
        "historical_sample": {
            "minimum_gap_pct": minimum_gap_pct,
            "research_lookback_days": research_lookback_days,
            "total": count_prior_gap_events(
                symbol=symbol,
                trade_date=trade_date,
                minimum_gap_pct=minimum_gap_pct,
                lookback_days=research_lookback_days,
            ),
            "directions": count_prior_gap_events_by_direction(
                symbol=symbol,
                trade_date=trade_date,
                minimum_gap_pct=minimum_gap_pct,
                lookback_days=research_lookback_days,
            ),
        },
    }
