# app/streamer/quote_streamer.py

import time
from datetime import datetime

from app.data_adapters.schwab_adapter import SchwabAdapter
from app.signals.spike_detector import SpikeDetector
from app.storage.sqlite_store import init_db, save_quote


adapter = SchwabAdapter()

detector = SpikeDetector(
    price_spike_pct=0.5,
    volume_spike_pct=5,
    window_size=5,
)

init_db()

SYMBOLS = ["AAPL", "TSLA", "NVDA"]


def stream_quotes():
    while True:
        for symbol in SYMBOLS:
            quote = adapter.get_quote(symbol)

            if quote is None:
                print(f"⚠️ No quote returned for {symbol}; skipping.")
                continue

            quote["timestamp"] = datetime.utcnow().isoformat()

            save_quote(quote)

            print("QUOTE:", quote)

            alerts = detector.process_quote(quote)

            for alert in alerts:
                print("🚨 ALERT:", alert)

        time.sleep(2)


if __name__ == "__main__":
    stream_quotes()