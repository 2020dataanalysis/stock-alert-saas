import json
from datetime import datetime, UTC
from pathlib import Path


TOKEN_FILE = Path(
    "/Users/ultrasupersam/apps/stock-alert-platform/2024schwab/private/refresh_token.json"
)

_token_cache = None
_cache_loaded_at = 0
CACHE_TTL_SECONDS = 5

def load_token_cache():
    global _token_cache
    global _cache_loaded_at

    now = int(datetime.now(UTC).timestamp())

    if (
        _token_cache is not None
        and now - _cache_loaded_at < CACHE_TTL_SECONDS
    ):
        return _token_cache

    if not TOKEN_FILE.exists():
        _token_cache = {
            "token_file_exists": False,
            "token_status": "MISSING",
            "access_token_expiration_time": 0,
            "refresh_token_expiration_time": 0,
            "expires_in": 0,
        }
        _cache_loaded_at = now
        return _token_cache

    with TOKEN_FILE.open() as f:
        token_data = json.load(f)

    _token_cache = {
        "token_file_exists": True,
        "access_token_expiration_time": int(
            token_data.get("access_token_expiration_time", 0)
        ),
        "refresh_token_expiration_time": int(
            token_data.get("refresh_token_expiration_time", 0)
        ),
        "expires_in": int(token_data.get("expires_in", 0)),
    }

    _cache_loaded_at = now
    return _token_cache



def refresh_token_cache():
    global _token_cache
    _token_cache = None
    return load_token_cache()


def get_token_status():
    token_data = load_token_cache()

    now = int(datetime.now(UTC).timestamp())

    access_exp = token_data["access_token_expiration_time"]
    refresh_exp = token_data["refresh_token_expiration_time"]


    access_expiry_display = (
        datetime.fromtimestamp(access_exp)
        .strftime("%Y-%m-%d %I:%M:%S %p")
    )

    refresh_expiry_display = (
        datetime.fromtimestamp(refresh_exp)
        .strftime("%Y-%m-%d %I:%M:%S %p")
    )



    access_remaining = max(0, access_exp - now)
    refresh_remaining = max(0, refresh_exp - now)

    if not token_data["token_file_exists"]:
        status = "MISSING"
    elif refresh_remaining <= 0:
        status = "REFRESH_TOKEN_EXPIRED"
    elif access_remaining <= 0:
        status = "ACCESS_TOKEN_EXPIRED"
    elif access_remaining < 300:
        status = "ACCESS_TOKEN_EXPIRING_SOON"
    elif refresh_remaining < 86400:
        status = "REFRESH_TOKEN_EXPIRING_SOON"
    else:
        status = "OK"

    return {
        "token_file_exists": token_data["token_file_exists"],
        "token_status": status,
        "expires_in": token_data["expires_in"],
        "access_token_expiration_time": access_exp,
        "refresh_token_expiration_time": refresh_exp,
        "access_token_seconds_remaining": access_remaining,
        "refresh_token_seconds_remaining": refresh_remaining,
        "access_token_expires_at": access_exp,
        "refresh_token_expires_at": refresh_exp,
        "access_token_expiry_display": access_expiry_display,
        "refresh_token_expiry_display": refresh_expiry_display,
    }