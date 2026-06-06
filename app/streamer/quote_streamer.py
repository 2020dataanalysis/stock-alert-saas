# app/streamer/quote_streamer.py

import time
from datetime import datetime, UTC
# from zoneinfo import ZoneInfo

from app.config import load_settings
from app.data_adapters.schwab_adapter import SchwabAdapter
# from app.storage.sqlite_store import init_db, save_quote, save_alert
from app.storage.sqlite_store import save_system_event
# from app.services.status_service import get_streamer_mode
from app.services.streamer_runtime_service import get_runtime_state
from app.signals.typed_rule_engine import evaluate_typed_rules
from app.services.token_status_service import get_token_status
from datetime import datetime, UTC, timedelta
from app.storage.sqlite_store import (
    init_db,
    get_connection,
    save_quote_with_connection,
    save_alert,
)
from app.services.watchlist_service import build_watchlist


from app.services.alert_rule_service import (
    delete_auto_generated_mover_rules,
    generate_mover_rules,
)

# PACIFIC = ZoneInfo("America/Los_Angeles")

settings = load_settings()

def log(message):
    timestamp = datetime.now(UTC).isoformat()
    print(f"{timestamp} {message}")

def create_adapter():
    return SchwabAdapter()


def refresh_access_token_by_time():
    adapter.client.oauth.get_access_token()
    remaining_seconds = None

    if remaining_seconds is None:
        log("⚠️ Access token remaining seconds unknown")
        return

    log(f"🔑 Access token seconds remaining: {remaining_seconds:.0f}")




adapter = create_adapter()
log("✅ Schwab adapter initialized")


service_running = True

FAILED_CYCLE_LIMIT = 3
failed_quote_cycles = 0

init_db()

POLL_SECONDS = settings["poll_seconds"]


startup_watchlist = build_watchlist()




def prepare_startup_mover_rules(startup_watchlist):

    if settings.get(
        "clear_existing_mover_alerts_on_startup"
    ):

        deleted = delete_auto_generated_mover_rules()

        log(
            f"🧹 Deleted {deleted} "
            f"old mover alert rules"
        )

    if settings.get(
        "auto_generate_mover_alerts"
    ):

        created = generate_mover_rules(
            startup_watchlist["movers"],
        )

        log(
            f"✅ Generated {created} "
            f"startup mover alert rules"
        )






prepare_startup_mover_rules(startup_watchlist)

if not startup_watchlist["symbols"]:
    save_system_event(
        event_type="STREAMER_START_FAILED",
        service="quote_streamer",
        status="ERROR",
        message="No symbols configured. Streamer exiting.",
        metadata={
            "favorite_symbols": startup_watchlist["favorites"],
            "mover_symbols": startup_watchlist["movers"],
        }
    )

    log("⚠️ No symbols configured. Exiting.")

    raise SystemExit(1)

save_system_event(
    event_type="STREAMER_STARTED",
    service="quote_streamer",
    status="ONLINE",
    message="Quote streamer started successfully",
    metadata={
        "favorite_symbols": startup_watchlist["favorites"],
        "mover_symbols": startup_watchlist["movers"],
        "symbols": startup_watchlist["symbols"],
        "poll_seconds": POLL_SECONDS,
    }
)











def handle_self_healing(
    successful_quotes,
    runtime,
):
    global failed_quote_cycles
    global adapter

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
                "token_status": token_status,
            },
        )

        log(
            f"⚠️ Provider degraded: "
            f"failed quote cycle {failed_quote_cycles}"
        )

        if token_status.get("token_status") == "ACCESS_TOKEN_EXPIRED":

            save_system_event(
                event_type="ACCESS_TOKEN_REFRESH",
                service="quote_streamer",
                status="WARNING",
                message="Refreshing expired access token",
                metadata=token_status,
            )

            log(
                "🔑 Access token expired. "
                "Refreshing token directly..."
            )

            try:

                adapter.client.oauth_client.refresh_token_grant_flow(
                    "REFRESH_TOKEN"
                )

                log("✅ Access token refreshed directly")

            except Exception as e:

                log(
                    f"FAILED TO REFRESH ACCESS TOKEN DIRECTLY: "
                    f"{type(e).__name__}: {e}"
                )

            failed_quote_cycles = 0

            return

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

            try:

                adapter = create_adapter()

                log(
                    "✅ Schwab adapter recreated "
                    "by self-healing"
                )

            except Exception as e:

                log(
                    f"FAILED TO RECREATE SCHWAB ADAPTER: "
                    f"{type(e).__name__}: {e}"
                )

            failed_quote_cycles = 0

    else:

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





def get_safe_runtime_state():
    try:
        return get_runtime_state(POLL_SECONDS)
    except Exception as e:
        log(f"FAILED TO GET RUNTIME STATE: {type(e).__name__}: {e}")

        return {
            "mode": "online",
            "session": "REGULAR",
            "should_fetch_quotes": True,
            "should_process_alerts": False,
            "sleep_seconds": POLL_SECONDS,
        }




def maybe_save_heartbeat(last_heartbeat, runtime):
    now = datetime.now(UTC)

    if (now - last_heartbeat) < timedelta(minutes=1):
        return last_heartbeat

    save_system_event(
        event_type="STREAMER_HEARTBEAT",
        service="quote_streamer",
        status="ONLINE",
        message="Streamer heartbeat",
        metadata={
            "mode": runtime["mode"],
            "session": runtime["session"],
        },
    )

    log("💓 Streamer heartbeat saved")

    return now


def get_current_watchlist():
    watchlist = build_watchlist()

    log(f"FAVORITE SYMBOLS: {watchlist['favorites']}")
    log(f"MOVERS WATCHLIST: {watchlist['movers']}")
    log(f"FINAL STREAM WATCHLIST: {watchlist['symbols']}")

    return watchlist




def save_quote_safely(quote_conn, quote):
    try:
        save_quote_with_connection(quote_conn, quote)
        quote_conn.commit()
        return quote_conn

    except Exception as e:
        log(f"FAILED TO SAVE QUOTE: {type(e).__name__}: {e}")

        try:
            quote_conn.close()
        except Exception:
            pass

        quote_conn = get_connection()

        log("✅ Recreated long-lived quote DB connection")

        return quote_conn





def process_symbol(
    symbol,
    runtime,
    quote_conn,
):
    quote = adapter.get_quote(symbol)

    if quote is None:

        log(f"⚠️ No quote returned for {symbol}; skipping.")

        return quote_conn, False

    quote["timestamp"] = datetime.now(UTC).isoformat()

    quote_conn = save_quote_safely(
        quote_conn,
        quote,
    )

    log(f"QUOTE: {quote}")

    if runtime["should_process_alerts"]:


        alerts = evaluate_typed_rules(quote)





        for alert in alerts:

            alert["timestamp"] = quote["timestamp"]

            log(f"🚨 ALERT: {alert}")

            save_alert(alert)

    return quote_conn, True



def stream_quotes():
    global service_running
    global failed_quote_cycles
    global adapter

    last_heartbeat = datetime.now(UTC)

    quote_conn = get_connection()

    log("✅ Long-lived quote DB connection opened")

    try:

        while service_running:

            runtime = get_safe_runtime_state()

            log(f"RUNTIME: {runtime}")


            if (
                runtime["session"] in ("CLOSED", "UNKNOWN")
            ):

                save_system_event(
                    event_type="STREAMER_EXITED",
                    service="quote_streamer",
                    status="EXITED",
                    message="Market closed. Streamer exited intentionally.",
                    metadata=runtime,
                )

                log("📴 Market closed. Stopping streamer.")

                service_running = False




            last_heartbeat = maybe_save_heartbeat(
                last_heartbeat,
                runtime,
            )

            if not runtime["should_fetch_quotes"]:

                time.sleep(runtime["sleep_seconds"])

                continue

            successful_quotes = 0

            refresh_access_token_by_time()

            watchlist = get_current_watchlist()

            for symbol in watchlist["symbols"]:

                quote_conn, success = process_symbol(
                    symbol,
                    runtime,
                    quote_conn,
                )

                if success:

                    successful_quotes += 1

            # TEMPORARILY DISABLED SELF-HEALING
            # handle_self_healing(
            #     successful_quotes,
            #     runtime,
            # )

            time.sleep(runtime["sleep_seconds"])

    finally:

        quote_conn.close()

        log("✅ Long-lived quote DB connection closed")




if __name__ == "__main__":
    stream_quotes()