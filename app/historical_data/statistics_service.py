from collections import defaultdict

from app.historical_data.repository import (
    get_historical_bars,
)


def group_bars_by_trading_day(bars):
    grouped = defaultdict(list)

    for bar in bars:
        trade_date = bar["timestamp"][:10]
        grouped[trade_date].append(bar)

    return grouped


def calculate_daily_opening_summary(
    symbol,
    lookback_limit=5000,
):
    bars = get_historical_bars(
        symbol=symbol,
        timeframe="1m",
        limit=lookback_limit,
    )

    grouped = group_bars_by_trading_day(
        bars
    )

    summaries = []

    for trade_date, day_bars in grouped.items():
        sorted_bars = sorted(
            day_bars,
            key=lambda row: row["timestamp"],
        )

        if not sorted_bars:
            continue

        open_bar = sorted_bars[0]
        close_bar = sorted_bars[-1]

        open_price = open_bar["open"]
        close_price = close_bar["close"]

        if not open_price:
            continue

        day_return_pct = (
            (close_price - open_price) /
            open_price
        ) * 100

        low_price = min(
            bar["low"]
            for bar in sorted_bars
        )

        high_price = max(
            bar["high"]
            for bar in sorted_bars
        )

        max_down_from_open_pct = (
            (low_price - open_price) /
            open_price
        ) * 100

        max_up_from_open_pct = (
            (high_price - open_price) /
            open_price
        ) * 100

        summaries.append({
            "symbol": symbol.upper(),
            "trade_date": trade_date,
            "open_price": open_price,
            "close_price": close_price,
            "day_return_pct": round(day_return_pct, 3),
            "max_down_from_open_pct": round(max_down_from_open_pct, 3),
            "max_up_from_open_pct": round(max_up_from_open_pct, 3),
            "minute_count": len(sorted_bars),
        })

    return {
        "symbol": symbol.upper(),
        "day_count": len(summaries),
        "days": summaries,
    }
