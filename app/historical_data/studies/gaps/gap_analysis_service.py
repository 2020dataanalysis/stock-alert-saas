import math

from app.historical_data.bars.repository import (
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



def calculate_gap_bucket_statistics(
    symbol,
    bucket_lower,
    bucket_upper,
    limit=500,
):
    gap_days = calculate_gap_days(
        symbol=symbol,
        limit=limit,
    )["days"]

    matching_days = [
        day
        for day in gap_days
        if day["gap_pct"] >= bucket_lower
        and day["gap_pct"] < bucket_upper
    ]

    if not matching_days:
        return {
            "symbol": symbol.upper(),
            "bucket_lower": bucket_lower,
            "bucket_upper": bucket_upper,
            "match_count": 0,
            "message": "No matching historical gap days found.",
        }

    day_returns = [
        (
            (day["day_close"] - day["open_price"]) /
            day["open_price"]
        ) * 100
        for day in matching_days
    ]

    max_downs = [
        (
            (day["day_low"] - day["open_price"]) /
            day["open_price"]
        ) * 100
        for day in matching_days
    ]

    max_ups = [
        (
            (day["day_high"] - day["open_price"]) /
            day["open_price"]
        ) * 100
        for day in matching_days
    ]

    red_day_count = sum(
        1
        for value in day_returns
        if value < 0
    )

    green_day_count = sum(
        1
        for value in day_returns
        if value > 0
    )

    return {
        "symbol": symbol.upper(),
        "bucket_lower": bucket_lower,
        "bucket_upper": bucket_upper,
        "match_count": len(matching_days),
        "average_day_return_pct": round(
            sum(day_returns) / len(day_returns),
            3,
        ),
        "average_max_down_from_open_pct": round(
            sum(max_downs) / len(max_downs),
            3,
        ),
        "average_max_up_from_open_pct": round(
            sum(max_ups) / len(max_ups),
            3,
        ),
        "green_day_count": green_day_count,
        "red_day_count": red_day_count,
        "green_day_pct": round(
            (green_day_count / len(matching_days)) * 100,
            1,
        ),
        "red_day_pct": round(
            (red_day_count / len(matching_days)) * 100,
            1,
        ),
        "matching_days": matching_days,
    }