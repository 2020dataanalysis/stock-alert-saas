# # app/data_adapters/movers_adapter.py

# class MoversAdapter:
#     def get_movers(self, symbol_id="EQUITY_ALL", sort="VOLUME", frequency=0):
#         pass



# app/data_adapters/movers_adapter.py

from app.data_adapters.schwab_adapter import SchwabAdapter


def get_mover_symbols(
    symbol_id="$DJI",
    sort="VOLUME",
    frequency=0,
    limit=10,
):
    adapter = SchwabAdapter()

    movers = adapter.get_movers(
        symbol_id=symbol_id,
        sort=sort,
        frequency=frequency,
    )

    if not movers:
        return []

    screeners = movers.get("screeners", [])

    symbols = [
        item["symbol"]
        for item in screeners[:limit]
        if item.get("symbol")
    ]

    return symbols