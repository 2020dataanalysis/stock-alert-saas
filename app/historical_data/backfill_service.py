from app.historical_data.import_service import (
    import_live_schwab_price_history,
)

DEFAULT_BACKFILL_SYMBOLS = [
    "TSLA",
    "NVDA",
    "AAPL",
    "MSFT",
    "AMZN",
    "WMT",
    "SPY",
    "QQQ",
]


def backfill_default_watchlist_intraday(
    period=10,
    frequency=1,
):
    return backfill_intraday_history(
        symbols=DEFAULT_BACKFILL_SYMBOLS,
        period=period,
        frequency=frequency,
    )

def backfill_intraday_history(
    symbols,
    period=10,
    frequency=1,
):
    results = []

    for symbol in symbols:
        result = import_live_schwab_price_history(
            symbol=symbol,
            period_type="day",
            period=period,
            frequency_type="minute",
            frequency=frequency,
            need_extended_hours_data=True,
            need_previous_close=True,
        )

        results.append(result)

    return {
        "status": "ok",
        "symbol_count": len(symbols),
        "results": results,
    }
