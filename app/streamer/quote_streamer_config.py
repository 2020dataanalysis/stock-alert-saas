# app/streamer/quote_streamer_config.py

import time
from datetime import datetime, UTC
from zoneinfo import ZoneInfo

from app.config import load_settings
from app.data_adapters.movers_adapter import get_mover_symbols
from app.data_adapters.schwab_adapter import SchwabAdapter
from app.signals.spike_detector import SpikeDetector
from app.storage.sqlite_store import init_db, save_quote, save_alert


PACIFIC = ZoneInfo("America/Los_Angeles")

settings = load_settings()

adapter = SchwabAdapter()

detector = SpikeDetector(
    price_spike_pct=settings["price_spike_pct"],
    volume_spike_pct=settings["volume_spike_pct"],
    window_size=settings["window_size"],
)

init_db()

favorite_symbols = settings["favorite_symbols"]

mover_symbols = []
if settings["use_movers"]:
    mover_symbols = get_mover_symbols(limit=settings["movers_limit"])

SYMBOLS = sorted(set(favorite_symbols + mover_symbols))

print("FAVORITE SYMBOLS:", favorite_symbols)
print("MOVERS WATCHLIST:", mover_symbols)
print("FINAL STREAM WATCHLIST:", SYMBOLS)

if not SYMBOLS:
    print("⚠️ No symbols configured. Exiting.")
    raise SystemExit(1)

POLL_SECONDS = settings["poll_seconds"]


def should_stop_streaming():
    now = datetime.now(PACIFIC)

    # Stop after 1:15 PM Pacific
    if now.hour > 13 or (now.hour == 13 and now.minute >= 15):
        return True

    return False


def stream_quotes():
    while True:
        if should_stop_streaming():
            print("Market session finished. Stopping streamer.")
            break

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