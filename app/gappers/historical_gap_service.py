from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any


def _calculate_gap_pct(
    open_price: float | None,
    previous_close: float | None,
) -> float | None:
    if open_price is None or previous_close in (None, 0):
        return None

    return (open_price - previous_close) * 100.0 / previous_close


def get_or_build_historical_gap_sample(
    symbol: str,
    minimum_gap_pct: float = 2.0,
    lookback_days: int = 365,
) -> dict[str, Any]:
    """
    Discover prior historical gaps for a symbol.

    V1 skeleton:
    - no Schwab fetch yet
    - no daily cache check yet
    - returns the agreed response shape
    """

    symbol = symbol.upper()
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=lookback_days)

    return {
        "symbol": symbol,
        "minimum_gap_pct": minimum_gap_pct,
        "lookback_days": lookback_days,
        "start_date": start_date.isoformat(),
        "end_date": today.isoformat(),
        "gap_count": 0,
        "gap_dates": [],
        "status": "not_implemented_yet",
    }


from app.gappers.storage import (
    get_daily_bar_coverage,
    get_daily_bars,
)


def get_daily_history_status(
    symbol: str,
    lookback_days: int = 365,
):
    symbol = symbol.upper()

    today = datetime.utcnow().date()
    required_start_date = today - timedelta(days=lookback_days)

    coverage = get_daily_bar_coverage(
        symbol
    )

    return {
        "symbol": symbol,
        "required_start_date": required_start_date.isoformat(),
        "required_end_date": today.isoformat(),
        "earliest_cached_date": coverage.get(
            "earliest_trade_date"
        ),
        "latest_cached_date": coverage.get(
            "latest_trade_date"
        ),
        "cached_rows": coverage.get(
            "count",
            0,
        ),
        "needs_import": (
            coverage.get("count", 0) == 0
            or coverage.get("earliest_trade_date") is None
            or coverage.get("latest_trade_date") is None
            or coverage.get("earliest_trade_date") > required_start_date.isoformat()
            or coverage.get("latest_trade_date") < today.isoformat()
        ),
    }


def _day_before(
    date_value: str,
) -> str:
    return (
        datetime.fromisoformat(date_value).date()
        - timedelta(days=1)
    ).isoformat()


def _day_after(
    date_value: str,
) -> str:
    return (
        datetime.fromisoformat(date_value).date()
        + timedelta(days=1)
    ).isoformat()


def get_missing_daily_history_ranges(
    symbol: str,
    lookback_days: int = 365,
):
    status = get_daily_history_status(
        symbol,
        lookback_days,
    )

    required_start = status["required_start_date"]
    required_end = status["required_end_date"]

    cached_start = status["earliest_cached_date"]
    cached_end = status["latest_cached_date"]

    missing_ranges = []

    if not cached_start or not cached_end:
        missing_ranges.append({
            "start_date": required_start,
            "end_date": required_end,
        })

        return {
            "needs_import": True,
            "missing_ranges": missing_ranges,
        }

    if cached_start > required_start:
        missing_ranges.append({
            "start_date": required_start,
            "end_date": _day_before(cached_start),
        })

    if cached_end < required_end:
        missing_ranges.append({
            "start_date": _day_after(cached_end),
            "end_date": required_end,
        })

    return {
        "needs_import": bool(missing_ranges),
        "missing_ranges": missing_ranges,
    }


def build_daily_history_import_plan(
    symbol: str,
    lookback_days: int = 365,
):
    missing = get_missing_daily_history_ranges(
        symbol,
        lookback_days,
    )

    return {
        "symbol": symbol.upper(),
        "lookback_days": lookback_days,
        "needs_import": missing["needs_import"],
        "ranges_to_import": missing[
            "missing_ranges"
        ],
        "status": "planned",
    }


from app.data_adapters.schwab_adapter import SchwabAdapter
from app.gappers.storage import (
    save_daily_bar,
    save_minute_bar,
    save_minute_bars,
    save_gap_event,
)


def _epoch_ms_to_trade_date(
    epoch_ms: int,
) -> str:
    return datetime.fromtimestamp(
        epoch_ms / 1000,
        tz=timezone.utc,
    ).date().isoformat()


def import_missing_daily_history(
    symbol: str,
    lookback_days: int = 365,
) -> dict[str, Any]:
    plan = build_daily_history_import_plan(
        symbol=symbol,
        lookback_days=lookback_days,
    )

    if not plan["needs_import"]:
        return {
            **plan,
            "status": "already_current",
            "imported_count": 0,
        }

    adapter = SchwabAdapter()

    response = adapter.client.market_data.get_price_history(
        symbol=symbol.upper(),
        period_type="year",
        period=1,
        frequency_type="daily",
        frequency=1,
        need_extended_hours_data=False,
        need_previous_close=True,
    )

    candles = response.get(
        "candles",
        [],
    )

    imported_count = 0

    for candle in candles:
        trade_date = _epoch_ms_to_trade_date(
            candle["datetime"]
        )

        save_daily_bar(
            symbol=symbol,
            trade_date=trade_date,
            open_price=candle.get("open"),
            high_price=candle.get("high"),
            low_price=candle.get("low"),
            close_price=candle.get("close"),
            volume=candle.get("volume"),
        )

        imported_count += 1

    return {
        **plan,
        "status": "imported",
        "imported_count": imported_count,
    }


def discover_historical_gaps(
    symbol: str,
    start_date: str,
    end_date: str,
    minimum_gap_pct: float = 2.0,
) -> dict[str, Any]:
    rows = get_daily_bars(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
    )

    gaps = []

    previous_row = None

    for row in rows:
        if previous_row is None:
            previous_row = row
            continue

        gap_pct = _calculate_gap_pct(
            open_price=row.get("open_price"),
            previous_close=previous_row.get("close_price"),
        )

        if gap_pct is None:
            previous_row = row
            continue

        if abs(gap_pct) >= minimum_gap_pct:
            gaps.append({
                "symbol": symbol.upper(),
                "trade_date": row["trade_date"],
                "previous_trade_date": previous_row["trade_date"],
                "previous_close": previous_row.get("close_price"),
                "open_price": row.get("open_price"),
                "gap_pct": round(gap_pct, 4),
                "gap_direction": "up" if gap_pct > 0 else "down",
                "volume": row.get("volume"),
            })

        previous_row = row

    return {
        "symbol": symbol.upper(),
        "start_date": start_date,
        "end_date": end_date,
        "minimum_gap_pct": minimum_gap_pct,
        "daily_bar_count": len(rows),
        "gap_count": len(gaps),
        "gaps": gaps,
    }


def save_discovered_historical_gaps(
    symbol: str,
    start_date: str,
    end_date: str,
    minimum_gap_pct: float = 2.0,
) -> dict[str, Any]:
    discovery = discover_historical_gaps(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        minimum_gap_pct=minimum_gap_pct,
    )

    saved_count = 0

    for gap in discovery["gaps"]:
        save_gap_event(
            symbol=gap["symbol"],
            trade_date=gap["trade_date"],
            detected_at=datetime.utcnow().isoformat(),
            gap_pct=gap["gap_pct"],
            gap_direction=gap["gap_direction"],
            previous_close=gap["previous_close"],
            open_price=gap["open_price"],
            last_price=None,
            volume=gap["volume"],
            is_shortable=None,
            hard_to_borrow=None,
            source="historical_daily",
        )

        saved_count += 1

    return {
        "symbol": symbol.upper(),
        "start_date": start_date,
        "end_date": end_date,
        "minimum_gap_pct": minimum_gap_pct,
        "discovered_count": discovery["gap_count"],
        "saved_count": saved_count,
    }


def _epoch_ms_to_iso(
    epoch_ms: int,
) -> str:
    return datetime.fromtimestamp(
        epoch_ms / 1000,
        tz=timezone.utc,
    ).isoformat()


def import_minute_bars_for_gap_day(
    symbol: str,
    trade_date: str,
) -> dict[str, Any]:
    adapter = SchwabAdapter()

    start_ms = int(
        datetime.fromisoformat(
            f"{trade_date}T00:00:00"
        ).replace(
            tzinfo=timezone.utc
        ).timestamp() * 1000
    )

    end_ms = int(
        datetime.fromisoformat(
            f"{trade_date}T23:59:59"
        ).replace(
            tzinfo=timezone.utc
        ).timestamp() * 1000
    )

    for frequency in [1, 5, 10, 15, 30]:
        response = adapter.client.market_data.get_price_history(
            symbol=symbol.upper(),
            period_type="day",
            period=10,
            frequency_type="minute",
            frequency=frequency,
            start_date=start_ms,
            end_date=end_ms,
            need_extended_hours_data=True,
            need_previous_close=True,
        )

        candles = response.get("candles", [])

        if not candles:
            continue

        bars = [
            {
                "symbol": symbol,
                "trade_date": trade_date,
                "bar_timestamp": _epoch_ms_to_iso(
                    candle["datetime"]
                ),
                "open_price": candle.get("open"),
                "high_price": candle.get("high"),
                "low_price": candle.get("low"),
                "close_price": candle.get("close"),
                "volume": candle.get("volume"),
            }
            for candle in candles
        ]

        imported_count = save_minute_bars(
            bars
        )

        return {
            "symbol": symbol.upper(),
            "trade_date": trade_date,
            "status": "imported",
            "frequency": frequency,
            "candles_imported": imported_count,
        }

    return {
        "symbol": symbol.upper(),
        "trade_date": trade_date,
        "status": "unavailable",
        "frequency": None,
        "candles_imported": 0,
    }


def import_minute_bars_for_historical_gaps(
    symbol: str,
    start_date: str,
    end_date: str,
    minimum_gap_pct: float = 2.0,
) -> dict[str, Any]:
    discovery = discover_historical_gaps(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        minimum_gap_pct=minimum_gap_pct,
    )

    results = []

    for gap in discovery["gaps"]:
        result = import_minute_bars_for_gap_day(
            symbol=symbol,
            trade_date=gap["trade_date"],
        )

        results.append(result)

    imported = [
        item for item in results
        if item["status"] == "imported"
    ]

    unavailable = [
        item for item in results
        if item["status"] == "unavailable"
    ]

    return {
        "symbol": symbol.upper(),
        "gap_count": discovery["gap_count"],
        "imported_days": len(imported),
        "unavailable_days": len(unavailable),
        "results": results,
    }
