# app/streamer/quote_streamer.py

import time
from app.data_adapters.schwab_adapter import SchwabAdapter

adapter = SchwabAdapter()

SYMBOLS = ["AAPL", "TSLA", "NVDA"]

def stream_quotes():
    while True:
        for symbol in SYMBOLS:
            quote = adapter.get_quote(symbol)
            print(quote)  # later → send to signal engine

        time.sleep(2)  # polling interval

if __name__ == "__main__":
    stream_quotes()