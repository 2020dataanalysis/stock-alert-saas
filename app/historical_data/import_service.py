from app.historical_data.repository import (
    init_historical_db,
)

from app.historical_data.schwab_importer import (
    import_price_history_candles,
)


def import_schwab_price_history_response(
    response_data,
    frequency_type,
    frequency,
):
    init_historical_db()

    symbol = response_data["symbol"]
    candles = response_data.get(
        "candles",
        []
    )

    return import_price_history_candles(
        symbol=symbol,
        candles=candles,
        frequency_type=frequency_type,
        frequency=frequency,
    )
