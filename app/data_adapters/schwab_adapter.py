from pathlib import Path
import sys
import json

from app.storage.sqlite_store import (
    save_provider_error,
    save_system_event,
)


PROJECT_PARENT = Path(__file__).resolve().parents[3]
SCHWAB_PATH = PROJECT_PARENT / "2024schwab"

if not SCHWAB_PATH.exists():
    raise RuntimeError(f"Schwab repo not found at: {SCHWAB_PATH}")

if str(SCHWAB_PATH) not in sys.path:
    sys.path.insert(0, str(SCHWAB_PATH))

from SchwabAPIClient import SchwabAPIClient






class SchwabAdapter:
    def __init__(self):
        self.client = SchwabAPIClient(
            credentials_file="credentials.json",
            grant_flow_type_filenames_file="grant_flow_type_filenames.json"
        )


        oauth_error = getattr(self.client.oauth_client, "last_oauth_error", None)

        if oauth_error:
            save_provider_error(
                provider="schwab",
                symbol=None,
                operation="oauth_refresh",
                error_type=oauth_error.get(
                    "error_type",
                    "refresh_token_authentication_error"
                ),
                message="Schwab OAuth refresh failed",
                raw_response=oauth_error,
            )

            save_system_event(
                event_type="SCHWAB_OAUTH_REFRESH_FAILED",
                service="schwab_adapter",
                status="ERROR",
                message=oauth_error.get("response_text"),
                metadata=oauth_error,
            )



        oauth_event = getattr(
            self.client.oauth_client,
            "last_oauth_event",
            None
        )

        if oauth_event:
            save_system_event(
                event_type=oauth_event.get(
                    "event_type",
                    "SCHWAB_OAUTH_EVENT"
                ),
                service="schwab_adapter",
                status="INFO",
                message=json.dumps(oauth_event),
                metadata=oauth_event,
            )






    def get_quote(self, symbol: str):
        data = self.client.get_ticker_data(symbol)

        if not data:
            save_provider_error(
                provider="schwab",
                symbol=symbol,
                operation="get_quote",
                error_type="empty_response",
                message=f"Schwab returned no data for {symbol}",
                raw_response=data,
            )
            return None

        if symbol not in data:
            save_provider_error(
                provider="schwab",
                symbol=symbol,
                operation="get_quote",
                error_type="missing_symbol",
                message=f"Schwab response missing symbol {symbol}",
                raw_response=data,
            )
            return None

        q = data[symbol]["quote"]
        ref = data[symbol].get("reference", {})

        return {
            "symbol": symbol,
            "bid": q.get("bidPrice"),
            "ask": q.get("askPrice"),
            "last": q.get("lastPrice"),
            "last_size": q.get("lastSize"),
            "volume": q.get("totalVolume"),
            "is_shortable": ref.get("isShortable"),
            "hard_to_borrow": ref.get("isHardToBorrow"),
            "htb_rate": ref.get("htbRate"),
        }

    def get_movers(self, symbol_id="$DJI", sort="VOLUME", frequency=0):
        base_url = "https://api.schwabapi.com/marketdata/v1"
        endpoint = f"/movers/{symbol_id}"

        params = {
            "sort": sort,
            "frequency": frequency,
        }

        response = self.client.get_request_endpoint(
            base_url,
            endpoint,
            params=params
        )

        # print("DEBUG RAW RESPONSE:", response)

        return response