from app.config import load_settings
from app.data_adapters.movers_adapter import get_mover_symbols
from app.storage.sqlite_store import save_mover_symbols


def acquire_movers(limit=None):
    if limit is None:
        settings = load_settings()
        limit = settings.get("movers_limit", 10)

    symbols = get_mover_symbols(limit=limit)

    if symbols:
        save_mover_symbols(symbols)

    return symbols
