from app.historical_data.imports.backfill_service import (
    DEFAULT_BACKFILL_SYMBOLS,
)

from app.historical_data.gap_opening_summary_service import (
    calculate_gap_opening_pattern_summary,
)


def summarize_gap_opening_statistics(
    stats,
):
    return {
        "symbol": stats["symbol"],
        "bucket_lower": stats["bucket_lower"],
        "bucket_upper": stats["bucket_upper"],
        "opening_minutes": stats["opening_minutes"],
        "match_count": stats["match_count"],
        "average_opening_return_pct": stats.get(
            "average_opening_return_pct"
        ),
        "average_opening_high_pct": stats.get(
            "average_opening_high_pct"
        ),
        "average_opening_low_pct": stats.get(
            "average_opening_low_pct"
        ),
        "positive_opening_pct": stats.get(
            "positive_opening_pct"
        ),
        "negative_opening_pct": stats.get(
            "negative_opening_pct"
        ),
    }


def calculate_watchlist_gap_opening_summary(
    bucket_lower,
    bucket_upper,
    opening_minutes=30,
    limit=500,
):
    results = []

    for symbol in DEFAULT_BACKFILL_SYMBOLS:
        stats = calculate_gap_opening_pattern_summary(
            symbol=symbol,
            bucket_lower=bucket_lower,
            bucket_upper=bucket_upper,
            opening_minutes=opening_minutes,
            limit=limit,
        )

        results.append(
            summarize_gap_opening_statistics(stats)
        )

    return {
        "bucket_lower": bucket_lower,
        "bucket_upper": bucket_upper,
        "opening_minutes": opening_minutes,
        "symbol_count": len(DEFAULT_BACKFILL_SYMBOLS),
        "results": results,
    }
