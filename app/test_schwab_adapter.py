from app.data_adapters.schwab_adapter import SchwabAdapter

adapter = SchwabAdapter()
quote = adapter.get_quote("AAPL")

print(quote)
