#!/usr/bin/env python3

import json
import sys
from datetime import datetime, timezone

from app.historical_data.bars.imports.backfill_service import (
    backfill_default_watchlist_daily,
    backfill_default_watchlist_intraday,
)


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def main():
    print(f"[{timestamp()}] Historical update started", flush=True)

    failures = []

    for name, operation in [
        ("daily", lambda: backfill_default_watchlist_daily(period=1)),
        (
            "intraday",
            lambda: backfill_default_watchlist_intraday(
                period=10,
                frequency=1,
            ),
        ),
    ]:
        print(f"[{timestamp()}] Starting {name} import", flush=True)

        try:
            response = operation()
            results = response.get("results", [])

            if response.get("status") != "ok" or len(results) != 8:
                failures.append(f"{name}: incomplete response")

            for result in results:
                print(
                    json.dumps({"type": name, **result}),
                    flush=True,
                )

                if (
                    result.get("status") != "ok"
                    or result.get("sdk_status") != "success"
                ):
                    failures.append(
                        f"{name}: {result.get('symbol', 'unknown')}"
                    )

        except Exception as error:
            print(
                f"[{timestamp()}] {name} exception: {error}",
                file=sys.stderr,
                flush=True,
            )
            failures.append(name)

    print(
        f"[{timestamp()}] Historical update completed. "
        f"Failures: {failures}",
        flush=True,
    )

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
