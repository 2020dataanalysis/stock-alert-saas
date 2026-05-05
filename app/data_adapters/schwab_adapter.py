from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[3]
SCHWAB_PATH = BASE_DIR / "2024schwab"

if str(SCHWAB_PATH) not in sys.path:
    sys.path.append(str(SCHWAB_PATH))

from SchwabAPIClient import SchwabAPIClient


class SchwabAdapter:
    def __init__(self):
        self.client = SchwabAPIClient(
            credentials_file="credentials.json",
            grant_flow_type_filenames_file="grant_flow_type_filenames.json"
        )

    def get_quote(self, symbol: str):
        data = self.client.get_ticker_data(symbol)

        if not data or symbol not in data:
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
