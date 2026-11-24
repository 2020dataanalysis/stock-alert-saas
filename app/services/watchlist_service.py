from app.config import load_settings


def assemble_watchlist(favorite_symbols, mover_symbols):
    symbols = sorted(set(favorite_symbols + mover_symbols))

    return {
        "favorites": favorite_symbols,
        "movers": mover_symbols,
        "symbols": symbols,
        "count": len(symbols),
    }


def build_watchlist():
    settings = load_settings()
    favorite_symbols = settings.get("favorite_symbols", [])
    mover_symbols = []

    if settings.get("use_movers"):
        from app.backend.mover_acquisition import acquire_movers

        mover_symbols = acquire_movers(
            limit=settings.get("movers_limit", 10)
        )

    return assemble_watchlist(
        favorite_symbols,
        mover_symbols,
    )


def load_watchlist():
    settings = load_settings()
    favorite_symbols = settings.get("favorite_symbols", [])
    mover_symbols = []

    if settings.get("use_movers"):
        from app.services.frontend_mover_service import get_fresh_mover_symbols

        mover_symbols = get_fresh_mover_symbols(
            limit=settings.get("movers_limit", 10)
        )

    return assemble_watchlist(
        favorite_symbols,
        mover_symbols,
    )


def get_symbol_source_badge(
    symbol,
    favorite_symbols,
    mover_symbols,
):
    if symbol in favorite_symbols:
        return "★"

    if symbol in mover_symbols:
        return "M"

    return ""
