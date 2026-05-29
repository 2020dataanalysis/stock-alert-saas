from datetime import datetime, timezone

from app.historical_data.repository import (
    upsert_historical_bar,
)


def epoch_ms_to_iso_datetime(epoch_ms):
    return datetime.fromtimestamp(
        epoch_ms / 1000,
        tz=timezone.utc,
    ).isoformat()


def normalize_timeframe(
    frequency_type,
    frequency,
):
    if frequency_type == "minute":
        return f"{frequency}m"

    if frequency_type == "daily":
        return "1d"

    if frequency_type == "weekly":
        return "1w"

    if frequency_type == "monthly":
        return "1mo"

    return f"{frequency}_{frequency_type}"


def import_price_history_candles(
    symbol,
    candles,
    frequency_type,
    frequency,
):
    timeframe = normalize_timeframe(
        frequency_type,
        frequency,
    )

    imported_count = 0

    for candle in candles:
        upsert_historical_bar(
            symbol=symbol.upper(),
            timestamp=epoch_ms_to_iso_datetime(
                candle["datetime"]
            ),
            timeframe=timeframe,
            open_price=candle["open"],
            high_price=candle["high"],
            low_price=candle["low"],
            close_price=candle["close"],
            volume=candle["volume"],
        )

        imported_count += 1

    return {
        "status": "ok",
        "symbol": symbol.upper(),
        "timeframe": timeframe,
        "imported_count": imported_count,
    }
