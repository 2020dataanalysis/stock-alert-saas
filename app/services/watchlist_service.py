from app.config import load_settings
from app.data_adapters.movers_adapter import get_mover_symbols


def build_watchlist():
    settings = load_settings()

    favorite_symbols = settings.get("favorite_symbols", [])

    mover_symbols = []

    if settings.get("use_movers"):

        mover_symbols = get_mover_symbols(
            limit=settings.get("movers_limit", 10)
        )

    symbols = sorted(
        set(favorite_symbols + mover_symbols)
    )

    return {
        "favorites": favorite_symbols,
        "movers": mover_symbols,
        "symbols": symbols,
        "count": len(symbols),
    }
