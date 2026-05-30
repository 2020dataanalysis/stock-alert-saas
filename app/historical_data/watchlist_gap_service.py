from app.historical_data.backfill_service import (
    DEFAULT_BACKFILL_SYMBOLS,
)

from app.historical_data.gap_analysis_service import (
    calculate_gap_bucket_statistics,
)


def calculate_watchlist_gap_statistics(
    bucket_lower,
    bucket_upper,
    limit=500,
):
    results = []

    for symbol in DEFAULT_BACKFILL_SYMBOLS:
        stats = calculate_gap_bucket_statistics(
            symbol=symbol,
            bucket_lower=bucket_lower,
            bucket_upper=bucket_upper,
            limit=limit,
        )

        results.append(stats)

    return {
        "bucket_lower": bucket_lower,
        "bucket_upper": bucket_upper,
        "symbol_count": len(DEFAULT_BACKFILL_SYMBOLS),
        "results": results,
    }
from app.historical_data.backfill_service import (
    DEFAULT_BACKFILL_SYMBOLS,
)

from app.historical_data.gap_analysis_service import (
    calculate_gap_bucket_statistics,
)


def summarize_gap_statistics(
    stats,
):
    return {
        "symbol": stats["symbol"],
        "bucket_lower": stats["bucket_lower"],
        "bucket_upper": stats["bucket_upper"],
        "match_count": stats["match_count"],
        "average_day_return_pct": stats.get(
            "average_day_return_pct"
        ),
        "average_max_down_from_open_pct": stats.get(
            "average_max_down_from_open_pct"
        ),
        "average_max_up_from_open_pct": stats.get(
            "average_max_up_from_open_pct"
        ),
        "green_day_pct": stats.get("green_day_pct"),
        "red_day_pct": stats.get("red_day_pct"),
    }


def calculate_watchlist_gap_statistics(
    bucket_lower,
    bucket_upper,
    limit=500,
):
    results = []

    for symbol in DEFAULT_BACKFILL_SYMBOLS:
        stats = calculate_gap_bucket_statistics(
            symbol=symbol,
            bucket_lower=bucket_lower,
            bucket_upper=bucket_upper,
            limit=limit,
        )

        results.append(
            summarize_gap_statistics(stats)
        )

    return {
        "bucket_lower": bucket_lower,
        "bucket_upper": bucket_upper,
        "symbol_count": len(DEFAULT_BACKFILL_SYMBOLS),
        "results": results,
    }