# app/streamer/quote_streamer.py

import time
from datetime import datetime, UTC
# from zoneinfo import ZoneInfo

from app.config import load_settings
from app.data_adapters.movers_adapter import get_mover_symbols
from app.data_adapters.schwab_adapter import SchwabAdapter
from app.signals.spike_detector import SpikeDetector
from app.storage.sqlite_store import init_db, save_quote, save_alert
from app.storage.sqlite_store import save_system_event
# from app.services.status_service import get_streamer_mode
from app.services.streamer_runtime_service import get_runtime_state
from app.signals.typed_rule_engine import evaluate_typed_rules
from app.services.token_status_service import get_token_status
from datetime import datetime, UTC, timedelta

# PACIFIC = ZoneInfo("America/Los_Angeles")

settings = load_settings()

def log(message):
    timestamp = datetime.now(UTC).isoformat()
    print(f"{timestamp} {message}")

def create_adapter():
    return SchwabAdapter()


adapter = create_adapter()
log("✅ Schwab adapter initialized")


detector = SpikeDetector(
    price_spike_pct=settings["price_spike_pct"],
    volume_spike_pct=settings["volume_spike_pct"],
    window_size=settings["window_size"],
)

service_running = True

FAILED_CYCLE_LIMIT = 3
failed_quote_cycles = 0

init_db()

favorite_symbols = settings["favorite_symbols"]

mover_symbols = []
if settings["use_movers"]:
    mover_symbols = get_mover_symbols(limit=settings["movers_limit"])


SYMBOLS = sorted(set(favorite_symbols + mover_symbols))
POLL_SECONDS = settings["poll_seconds"]

log(f"FAVORITE SYMBOLS: {favorite_symbols}")
log(f"MOVERS WATCHLIST: {mover_symbols}")
log(f"FINAL STREAM WATCHLIST: {SYMBOLS}")

if not SYMBOLS:
    save_system_event(
        event_type="STREAMER_START_FAILED",
        service="quote_streamer",
        status="ERROR",
        message="No symbols configured. Streamer exiting.",
        metadata={
            "favorite_symbols": favorite_symbols,
            "mover_symbols": mover_symbols,
        },
    )

    log("⚠️ No symbols configured. Exiting.")

    raise SystemExit(1)

save_system_event(
    event_type="STREAMER_STARTED",
    service="quote_streamer",
    status="ONLINE",
    message="Quote streamer started successfully",
    metadata={
        "favorite_symbols": favorite_symbols,
        "mover_symbols": mover_symbols,
        "symbols": SYMBOLS,
        "poll_seconds": POLL_SECONDS,
    },
)


def stream_quotes():
    global service_running
    global failed_quote_cycles
    global adapter

    last_heartbeat = datetime.now(UTC)

    while service_running:
        try:
            runtime = get_runtime_state(POLL_SECONDS)

        except Exception as e:
            log(
                f"FAILED TO GET RUNTIME STATE: "
                f"{type(e).__name__}: {e}"
            )

            runtime = {
                "mode": "online",
                "session": "REGULAR",
                "should_fetch_quotes": True,
                "should_process_alerts": False,
                "sleep_seconds": POLL_SECONDS,
            }

        log(f"RUNTIME: {runtime}")



        now = datetime.now(UTC)

        if (now - last_heartbeat) >= timedelta(minutes=1):
            try:
                save_system_event(
                    event_type="STREAMER_HEARTBEAT",
                    service="quote_streamer",
                    status="ONLINE",
                    message="Streamer heartbeat alive",
                )

            except Exception as e:
                log(
                    f"FAILED TO SAVE HEARTBEAT: "
                    f"{type(e).__name__}: {e}"
                )


            last_heartbeat = now




        if not runtime["should_fetch_quotes"]:
            time.sleep(runtime["sleep_seconds"])
            continue

        successful_quotes = 0

        for symbol in SYMBOLS:
            quote = adapter.get_quote(symbol)

            if quote is None:
                log(f"⚠️ No quote returned for {symbol}; skipping.")
                continue

            successful_quotes += 1

            quote["timestamp"] = datetime.now(UTC).isoformat()

            try:
                save_quote(quote)

            except Exception as e:
                log(
                    f"FAILED TO SAVE QUOTE: "
                    f"{type(e).__name__}: {e}"
                )

            log(f"QUOTE: {quote}")



            if runtime["should_process_alerts"]:
                alerts = []

                # legacy detector
                alerts.extend(detector.process_quote(quote))

                # typed rule engine
                # alerts.extend(evaluate_typed_rules(quote))
                # typed rule engine
                try:
                    alerts.extend(evaluate_typed_rules(quote))

                except Exception as e:
                    log(
                        f"FAILED TO EVALUATE TYPED RULES: "
                        f"{type(e).__name__}: {e}"
                    )




                for alert in alerts:
                    alert["timestamp"] = quote["timestamp"]

                    log(f"🚨 ALERT: {alert}")

                    save_alert(alert)

        # provider degradation detection
        if successful_quotes == 0:
            failed_quote_cycles += 1

            token_status = get_token_status()

            save_system_event(
                event_type="PROVIDER_DEGRADED",
                service="quote_streamer",
                status="WARNING",
                message="Quote cycle returned zero successful quotes",
                metadata={
                    "failed_quote_cycles": failed_quote_cycles,
                    "symbols": SYMBOLS,
                    "token_status": token_status,
                },
            )

            log(
                f"⚠️ Provider degraded: "
                f"failed quote cycle {failed_quote_cycles}"
            )

            # token-aware recovery
            if token_status.get("token_status") == "EXPIRED":

                save_system_event(
                    event_type="ACCESS_TOKEN_REFRESH",
                    service="quote_streamer",
                    status="WARNING",
                    message="Refreshing expired access token",
                    metadata=token_status,
                )

                log("🔑 Access token expired. Refreshing token directly...")

                try:
                    adapter.client.oauth_client.refresh_token_grant_flow("REFRESH_TOKEN")
                    log("✅ Access token refreshed directly")

                except Exception as e:
                    log(
                        f"FAILED TO REFRESH ACCESS TOKEN DIRECTLY: "
                        f"{type(e).__name__}: {e}"
                    )

                failed_quote_cycles = 0

                continue




            # generic self-healing recovery
            if failed_quote_cycles >= FAILED_CYCLE_LIMIT:

                save_system_event(
                    event_type="PROVIDER_SELF_HEALING_RESTART",
                    service="quote_streamer",
                    status="WARNING",
                    message=(
                        "Recreating Schwab adapter after "
                        "repeated failed quote cycles"
                    ),
                    metadata={
                        "failed_quote_cycles": failed_quote_cycles,
                    },
                )

                log("🔄 Recreating Schwab adapter...")

                # adapter = create_adapter()
                log("⚠️ Skipping adapter recreation for now to avoid file-handle leak")

                failed_quote_cycles = 0

        else:
            # recovery detection
            if failed_quote_cycles > 0:

                save_system_event(
                    event_type="PROVIDER_RECOVERED",
                    service="quote_streamer",
                    status="OK",
                    message="Quote provider recovered after failed cycles",
                    metadata={
                        "successful_quotes": successful_quotes,
                    },
                )

                log(
                    f"✅ Provider recovered with "
                    f"{successful_quotes} successful quotes"
                )

            failed_quote_cycles = 0

        time.sleep(runtime["sleep_seconds"])


if __name__ == "__main__":
    stream_quotes()