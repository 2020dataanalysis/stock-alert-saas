from datetime import datetime, timezone
from app.historical_data.repository import (
    upsert_historical_bars,
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

    rows = []

    for candle in candles:
        rows.append((
            symbol.upper(),
            epoch_ms_to_iso_datetime(
                candle["datetime"]
            ),
            timeframe,
            candle["open"],
            candle["high"],
            candle["low"],
            candle["close"],
            candle["volume"],
        ))

    imported_count = upsert_historical_bars(
        rows
    )

    return {
        "status": "ok",
        "symbol": symbol.upper(),
        "timeframe": timeframe,
        "imported_count": imported_count,
    }