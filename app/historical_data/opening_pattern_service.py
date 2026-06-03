from collections import defaultdict

from app.historical_data.bars.repository import (
    get_historical_bars,
)


def group_intraday_bars_by_date(
    bars,
):
    grouped = defaultdict(list)

    for bar in bars:
        trade_date = bar["timestamp"][:10]
        grouped[trade_date].append(bar)

    return grouped


def calculate_opening_behavior_for_day(
    symbol,
    trade_date,
    bars,
    opening_minutes=30,
):
    sorted_bars = sorted(
        bars,
        key=lambda bar: bar["timestamp"],
    )

    opening_bars = sorted_bars[:opening_minutes]

    if not opening_bars:
        return None

    open_price = opening_bars[0]["open"]
    opening_high = max(
        bar["high"]
        for bar in opening_bars
    )
    opening_low = min(
        bar["low"]
        for bar in opening_bars
    )
    final_opening_close = opening_bars[-1]["close"]

    if not open_price:
        return None

    opening_return_pct = (
        (final_opening_close - open_price) /
        open_price
    ) * 100

    opening_high_pct = (
        (opening_high - open_price) /
        open_price
    ) * 100

    opening_low_pct = (
        (opening_low - open_price) /
        open_price
    ) * 100

    return {
        "symbol": symbol.upper(),
        "trade_date": trade_date,
        "opening_minutes": opening_minutes,
        "open_price": open_price,
        "opening_return_pct": round(opening_return_pct, 3),
        "opening_high_pct": round(opening_high_pct, 3),
        "opening_low_pct": round(opening_low_pct, 3),
        "opening_high": opening_high,
        "opening_low": opening_low,
        "final_opening_close": final_opening_close,
    }


def calculate_opening_patterns(
    symbol,
    opening_minutes=30,
    limit=20000,
):
    bars = get_historical_bars(
        symbol=symbol,
        timeframe="1m",
        limit=limit,
    )

    grouped = group_intraday_bars_by_date(
        bars
    )

    patterns = []

    for trade_date, day_bars in grouped.items():
        pattern = calculate_opening_behavior_for_day(
            symbol=symbol,
            trade_date=trade_date,
            bars=day_bars,
            opening_minutes=opening_minutes,
        )

        if pattern:
            patterns.append(pattern)

    patterns = sorted(
        patterns,
        key=lambda row: row["trade_date"],
    )

    return {
        "symbol": symbol.upper(),
        "opening_minutes": opening_minutes,
        "day_count": len(patterns),
        "patterns": patterns,
    }
