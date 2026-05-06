# app/streamer/quote_streamer_config.py

import time
from datetime import datetime, UTC

from app.config import load_settings
from app.data_adapters.schwab_adapter import SchwabAdapter
from app.signals.spike_detector import SpikeDetector
from app.storage.sqlite_store import init_db, save_quote, save_alert


settings = load_settings()

adapter = SchwabAdapter()

detector = SpikeDetector(
    price_spike_pct=settings["price_spike_pct"],
    volume_spike_pct=settings["volume_spike_pct"],
    window_size=settings["window_size"],
)

init_db()

SYMBOLS = settings["symbols"]
POLL_SECONDS = settings["poll_seconds"]


def stream_quotes():
    while True:
        for symbol in SYMBOLS:
            quote = adapter.get_quote(symbol)

            if quote is None:
                print(f"⚠️ No quote returned for {symbol}; skipping.")
                continue

            quote["timestamp"] = datetime.now(UTC).isoformat()

            save_quote(quote)

            print("QUOTE:", quote)

            alerts = detector.process_quote(quote)

            for alert in alerts:
                alert["timestamp"] = quote["timestamp"]
                print("🚨 ALERT:", alert)
                save_alert(alert)

        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    stream_quotes()