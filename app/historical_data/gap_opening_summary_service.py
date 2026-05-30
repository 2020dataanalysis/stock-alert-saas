from app.historical_data.gap_analysis_service import (
    calculate_gap_days,
)

from app.historical_data.opening_pattern_service import (
    calculate_opening_patterns,
)


def calculate_gap_opening_pattern_summary(
    symbol,
    bucket_lower,
    bucket_upper,
    opening_minutes=30,
    limit=500,
):
    gap_days = calculate_gap_days(
        symbol=symbol,
        limit=limit,
    )["days"]

    opening_patterns = calculate_opening_patterns(
        symbol=symbol,
        opening_minutes=opening_minutes,
        limit=50000,
    )["patterns"]

    patterns_by_date = {
        pattern["trade_date"]: pattern
        for pattern in opening_patterns
    }

    matching_days = []

    for gap_day in gap_days:
        gap_pct = gap_day["gap_pct"]

        if gap_pct < bucket_lower:
            continue

        if gap_pct >= bucket_upper:
            continue

        trade_date = gap_day["trade_date"]
        opening_pattern = patterns_by_date.get(
            trade_date
        )

        if not opening_pattern:
            continue

        matching_days.append({
            **gap_day,
            "opening_pattern": opening_pattern,
        })

    if not matching_days:
        return {
            "symbol": symbol.upper(),
            "bucket_lower": bucket_lower,
            "bucket_upper": bucket_upper,
            "opening_minutes": opening_minutes,
            "match_count": 0,
            "message": "No matching gap/opening pattern days found.",
        }

    opening_returns = [
        day["opening_pattern"]["opening_return_pct"]
        for day in matching_days
    ]

    opening_highs = [
        day["opening_pattern"]["opening_high_pct"]
        for day in matching_days
    ]

    opening_lows = [
        day["opening_pattern"]["opening_low_pct"]
        for day in matching_days
    ]

    positive_opening_count = sum(
        1
        for value in opening_returns
        if value > 0
    )

    negative_opening_count = sum(
        1
        for value in opening_returns
        if value < 0
    )

    return {
        "symbol": symbol.upper(),
        "bucket_lower": bucket_lower,
        "bucket_upper": bucket_upper,
        "opening_minutes": opening_minutes,
        "match_count": len(matching_days),
        "average_opening_return_pct": round(
            sum(opening_returns) / len(opening_returns),
            3,
        ),
        "average_opening_high_pct": round(
            sum(opening_highs) / len(opening_highs),
            3,
        ),
        "average_opening_low_pct": round(
            sum(opening_lows) / len(opening_lows),
            3,
        ),
        "positive_opening_count": positive_opening_count,
        "negative_opening_count": negative_opening_count,
        "positive_opening_pct": round(
            (positive_opening_count / len(matching_days)) * 100,
            1,
        ),
        "negative_opening_pct": round(
            (negative_opening_count / len(matching_days)) * 100,
            1,
        ),
        "matching_days": matching_days,
    }
