import sys

from app.backend.market_hours_acquisition import acquire_market_hours
from app.backend.mover_acquisition import acquire_movers
from app.storage.sqlite_store import save_provider_error


def run_market_hours_acquisition(interactive_auth=False):
    try:
        market_hours = acquire_market_hours(
            interactive_auth=interactive_auth,
        )

        print(
            f"Market hours saved: {market_hours['date']}",
            flush=True,
        )

        return True

    except Exception as error:
        save_provider_error(
            provider="schwab",
            operation="acquire_market_hours",
            error_type=type(error).__name__,
            message=str(error),
        )

        print(
            f"Market hours acquisition failed: "
            f"{type(error).__name__}",
            flush=True,
        )

        return False


def run_mover_acquisition():
    try:
        symbols = acquire_movers()

        if not symbols:
            raise RuntimeError("No movers returned")

        print(
            f"Movers saved: {len(symbols)}",
            flush=True,
        )

        return True

    except Exception as error:
        save_provider_error(
            provider="schwab",
            operation="acquire_movers",
            error_type=type(error).__name__,
            message=str(error),
        )

        print(
            f"Mover acquisition failed: "
            f"{type(error).__name__}",
            flush=True,
        )

        return False


def main():
    run_market_hours_acquisition(
        interactive_auth=sys.stdin.isatty(),
    )
    run_mover_acquisition()


if __name__ == "__main__":
    main()
