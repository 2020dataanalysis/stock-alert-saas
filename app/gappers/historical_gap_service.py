from __future__ import annotations

from datetime import datetime, timedelta
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
