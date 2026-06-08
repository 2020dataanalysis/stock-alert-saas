from __future__ import annotations

from typing import Any

from app.config import load_settings
from app.data_adapters.movers_adapter import get_mover_symbols
from app.data_adapters.schwab_adapter import SchwabAdapter


def _calculate_gap_pct(open_price: float | None, previous_close: float | None) -> float | None:
    if open_price is None or previous_close in (None, 0):
        return None

    return (open_price - previous_close) * 100.0 / previous_close


def get_live_gappers(
    minimum_gap_pct: float = 2.0,
    limit: int | None = None,
) -> dict[str, Any]:
    settings = load_settings()
    movers_limit = limit or settings.get("movers_limit", 10)

    mover_symbols = get_mover_symbols(limit=movers_limit)
    adapter = SchwabAdapter()

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

        rows.append(
            {
                "symbol": symbol,
                "gap_pct": round(gap_pct, 4),
                "direction": "up" if gap_pct > 0 else "down",
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
