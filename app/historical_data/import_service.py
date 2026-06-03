import json
from pathlib import Path
import time
from datetime import datetime, timezone

from schwab_client import SchwabClient

from app.historical_data.bars.repository import (
    init_historical_db,
)

from app.historical_data.schwab_importer import (
    import_price_history_candles,
)


BASE_DIR = Path(__file__).resolve().parents[2]

SCHWAB_CLIENT_REPO_PATH = (
    BASE_DIR.parent / "schwab-api-client"
)

CREDENTIALS_FILE = (
    SCHWAB_CLIENT_REPO_PATH / "private" / "credentials.json"
)

TOKEN_FILE = (
    SCHWAB_CLIENT_REPO_PATH / "private" / "refresh_token.json"
)


def load_schwab_credentials():
    with open(CREDENTIALS_FILE, "r") as file:
        return json.load(file)


def get_schwab_client():
    credentials = load_schwab_credentials()

    return SchwabClient(
        app_key=credentials["app_key"],
        app_secret=credentials["app_secret"],
        redirect_uri=credentials["redirect_uri"],
        token_file=TOKEN_FILE,
    )


def import_schwab_price_history_response(
    response_data,
    frequency_type,
    frequency,
):
    init_historical_db()

    symbol = response_data["symbol"]
    candles = response_data.get(
        "candles",
        []
    )

    return import_price_history_candles(
        symbol=symbol,
        candles=candles,
        frequency_type=frequency_type,
        frequency=frequency,
    )


def import_live_schwab_price_history(
    symbol,
    period_type="day",
    period=10,
    frequency_type="minute",
    frequency=1,
    need_extended_hours_data=True,
    need_previous_close=True,
):
    started_at = time.time()

    try:
        client = get_schwab_client()

        response_data = client.market_data.get_price_history(
            symbol=symbol,
            period_type=period_type,
            period=period,
            frequency_type=frequency_type,
            frequency=frequency,
            need_extended_hours_data=need_extended_hours_data,
            need_previous_close=need_previous_close,
        )

        result = import_schwab_price_history_response(
            response_data=response_data,
            frequency_type=frequency_type,
            frequency=frequency,
        )

        result["sdk_status"] = "success"
        result["sdk_duration_seconds"] = round(
            time.time() - started_at,
            3,
        )
        result["sdk_checked_at"] = datetime.now(
            timezone.utc
        ).isoformat()

        return result

    except Exception as error:
        return {
            "status": "error",
            "sdk_status": "failure",
            "symbol": symbol.upper(),
            "operation": "get_price_history",
            "error": str(error),
            "sdk_duration_seconds": round(
                time.time() - started_at,
                3,
            ),
            "sdk_checked_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }