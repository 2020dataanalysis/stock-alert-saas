from __future__ import annotations

from typing import Any

from app.gappers.storage import (
    get_gap_event_by_id,
    save_gap_outcome,
)


def calculate_gap_outcome(
    gap_event_id: int,
) -> dict[str, Any]:
    event = get_gap_event_by_id(
        gap_event_id
    )

    if not event:
        return {
            "found": False,
        }

    outcome = save_gap_outcome(
        gap_event_id=gap_event_id,
        filled=None,
        fill_timestamp=None,
        minutes_to_fill=None,
        max_run_pct=None,
        max_drop_pct=None,
        close_result_pct=None,
    )

    return {
        "found": True,
        "event": event,
        "outcome": outcome,
    }
