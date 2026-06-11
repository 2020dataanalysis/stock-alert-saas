"""
On-Demand Market Data History Service

Purpose:
    Fetch live/on-demand historical market data from Schwab.

Important:
    This module does not write to the historical database.
    Fetching market data and storing market data are intentionally separate.

Consumers:
    - Browser/API routes
    - Historical importers
    - Replay tools
    - Scalp State analysis
    - Statistics / future ML pipelines
"""

from datetime import datetime, timezone
import time

from app.historical_data.bars.imports.import_service import (
    get_schwab_client,
)


SUPPORTED_INTERVALS = {
    "1m": ("minute", 1),
    "5m": ("minute", 5),
    "10m": ("minute", 10),
    "15m": ("minute", 15),
    "30m": ("minute", 30),
    "1d": ("daily", 1),
}


def resolve_interval(
    interval: str,
):
    normalized_interval = interval.lower().strip()

    if normalized_interval not in SUPPORTED_INTERVALS:
        raise ValueError(
            f"Unsupported interval '{interval}'. "
            f"Supported intervals: {', '.join(SUPPORTED_INTERVALS.keys())}"
        )

    frequency_type, frequency = SUPPORTED_INTERVALS[
        normalized_interval
    ]

    return frequency_type, frequency


def resolve_period_from_request(
    days: int | None,
    start_date: str | None,
    end_date: str | None,
):
    """
    Normalize browser/API request parameters into Schwab-compatible
    period settings.

    Current implementation:
        - days=N maps to Schwab period_type='day', period=N
        - explicit dates are accepted for API ergonomics but still mapped
          to the calendar day span for now.

    Future:
        If the Schwab client supports explicit start/end datetime arguments,
        this function should become the adapter boundary for that conversion.
    """

    if start_date or end_date:
        if not start_date or not end_date:
            raise ValueError(
                "start_date and end_date must be provided together."
            )

        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()

        if end < start:
            raise ValueError(
                "end_date must be greater than or equal to start_date."
            )

        resolved_days = (end - start).days + 1

        return {
            "request_mode": "date_range",
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "period_type": "day",
            "period": resolved_days,
        }

    resolved_days = days or 1

    if resolved_days < 1:
        raise ValueError(
            "days must be greater than or equal to 1."
        )

    return {
        "request_mode": "days",
        "days": resolved_days,
        "period_type": "day",
        "period": resolved_days,
    }


def fetch_price_history(
    symbol: str,
    days: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    interval: str = "1m",
    need_extended_hours_data: bool = True,
    need_previous_close: bool = True,
):
    """
    Fetch raw Schwab price history.

    This intentionally returns the Schwab response plus metadata.
    It does not import candles into any local database.
    """

    started_at = time.time()

    symbol = symbol.upper().strip()
    frequency_type, frequency = resolve_interval(
        interval
    )
    period_settings = resolve_period_from_request(
        days=days,
        start_date=start_date,
        end_date=end_date,
    )

    client = get_schwab_client()

    response_data = client.market_data.get_price_history(
        symbol=symbol,
        period_type=period_settings["period_type"],
        period=period_settings["period"],
        frequency_type=frequency_type,
        frequency=frequency,
        need_extended_hours_data=need_extended_hours_data,
        need_previous_close=need_previous_close,
    )

    candles = response_data.get(
        "candles",
        []
    )

    return {
        "status": "success",
        "source": "schwab",
        "symbol": symbol,
        "interval": interval,
        "frequency_type": frequency_type,
        "frequency": frequency,
        "request": period_settings,
        "candle_count": len(candles),
        "candles": candles,
        "raw": response_data,
        "duration_seconds": round(
            time.time() - started_at,
            3,
        ),
        "checked_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }
