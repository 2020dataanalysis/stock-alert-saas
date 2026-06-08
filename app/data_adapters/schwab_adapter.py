from pathlib import Path
import sys
import json

from app.storage.sqlite_store import (
    save_provider_error,
    save_system_event,
)


PROJECT_PARENT = Path(__file__).resolve().parents[3]
SCHWAB_PATH = PROJECT_PARENT / "schwab-api-client"

if not SCHWAB_PATH.exists():
    raise RuntimeError(f"Schwab repo not found at: {SCHWAB_PATH}")

if str(SCHWAB_PATH) not in sys.path:
    sys.path.insert(0, str(SCHWAB_PATH))

from schwab_client.client import SchwabClient






class SchwabAdapter:
    def __init__(self):
        credentials_file = SCHWAB_PATH / "private" / "credentials.json"
        token_file = SCHWAB_PATH / "private" / "refresh_token.json"

        with credentials_file.open() as f:
            credentials = json.load(f)

        self.client = SchwabClient(
            app_key=credentials["app_key"],
            app_secret=credentials["app_secret"],
            redirect_uri=credentials["redirect_uri"],
            token_file=token_file,
        )




    def get_quote(self, symbol: str):
        data = self.client.market_data.get_quote(symbol)

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
            "open": q.get("openPrice"),
            "previous_close": q.get("closePrice"),
            "net_change": q.get("netChange"),
            "net_percent_change": q.get("netPercentChange"),
            "is_shortable": ref.get("isShortable"),
            "hard_to_borrow": ref.get("isHardToBorrow"),
            "htb_rate": ref.get("htbRate"),
        }

    def get_movers(self, symbol_id="$DJI", sort="VOLUME", frequency=0):
        return self.client.market_data.get_movers(
            symbol_id=symbol_id,
            sort=sort,
            frequency=frequency,
        )

    def get_market_hours(self, market_id="equity"):
        return self.client.market_data.get_market_hours(
            markets=market_id,
        )
