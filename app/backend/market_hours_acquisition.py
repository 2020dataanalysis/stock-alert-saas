from app.data_adapters.schwab_adapter import SchwabAdapter
from app.storage.sqlite_store import save_market_hours


def acquire_market_hours(interactive_auth=False):
    adapter = SchwabAdapter(interactive_auth=interactive_auth)
    response = adapter.get_market_hours("equity")

    if not isinstance(response, dict):
        raise RuntimeError("Invalid market hours response")

    market_hours = response.get("equity", {}).get("EQ")

    if not isinstance(market_hours, dict):
        raise RuntimeError("Missing equity market hours")

    if not isinstance(market_hours.get("isOpen"), bool):
        raise RuntimeError("Missing market open status")

    save_market_hours(market_hours)

    return market_hours
