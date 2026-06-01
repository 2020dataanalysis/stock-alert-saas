# app/config.py

import json
from pathlib import Path

DEFAULT_SETTINGS = {
    "favorite_symbols": ["AAPL", "TSLA", "NVDA"],
    "use_movers": True,
    "movers_limit": 10,
    "price_spike_pct": 0.5,
    "volume_spike_pct": 5,
    "window_size": 5,
    "poll_seconds": 1,
}


def load_settings(config_path="config/settings.json"):
    path = Path(config_path)

    if not path.exists():
        return DEFAULT_SETTINGS.copy()

    with path.open("r") as f:
        user_settings = json.load(f)

    settings = DEFAULT_SETTINGS.copy()
    settings.update(user_settings)

    return settings