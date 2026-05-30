import math

from app.historical_data.repository import (
    get_historical_bars,
)


def calculate_gap_pct(
    open_price,
    previous_close,
):
    if not previous_close:
        return None

    return (
        (open_price - previous_close) /
        previous_close
    ) * 100


def classify_gap_bucket(
    gap_pct,
    bucket_size=0.5,
):
    if gap_pct is None:
        return None

    lower = math.floor(gap_pct / bucket_size) * bucket_size
    upper = lower + bucket_size

    return {
        "lower": round(lower, 2),
        "upper": round(upper, 2),
        "label": f"{round(lower, 2)}% to {round(upper, 2)}%",
    }


def get_daily_bars_chronological(
    symbol,
    limit=500,
):
    bars = get_historical_bars(
        symbol=symbol,
        timeframe="1d",
        limit=limit,
    )

    return sorted(
        bars,
        key=lambda bar: bar["timestamp"],
    )


def calculate_gap_days(
    symbol,
    limit=500,
):
    daily_bars = get_daily_bars_chronological(
        symbol=symbol,
        limit=limit,
    )

    results = []

    for index in range(1, len(daily_bars)):
        previous_bar = daily_bars[index - 1]
        current_bar = daily_bars[index]

        previous_close = previous_bar["close"]
        open_price = current_bar["open"]

        gap_pct = calculate_gap_pct(
            open_price=open_price,
            previous_close=previous_close,
        )

        bucket = classify_gap_bucket(
            gap_pct
        )

        results.append({
            "symbol": symbol.upper(),
            "trade_date": current_bar["timestamp"][:10],
            "previous_close": previous_close,
            "open_price": open_price,
            "gap_pct": round(gap_pct, 3),
            "gap_bucket": bucket,
            "day_close": current_bar["close"],
            "day_high": current_bar["high"],
            "day_low": current_bar["low"],
        })

    return {
        "symbol": symbol.upper(),
        "day_count": len(results),
        "days": results,
    }
