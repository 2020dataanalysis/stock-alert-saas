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
