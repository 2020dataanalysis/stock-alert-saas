from app.data_adapters.schwab_adapter import SchwabAdapter

adapter = SchwabAdapter()

movers = adapter.get_movers(
    symbol_id="$DJI",
    sort="VOLUME",
    frequency=0,
)

for item in movers.get("screeners", []):
    print(
        item["symbol"],
        item["description"],
        "price:", item["lastPrice"],
        "change:", round(item["netPercentChange"] * 100, 2),
        "%",
        "volume:", item["volume"],
    )