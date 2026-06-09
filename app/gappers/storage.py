from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any

from app.gappers.db_init import get_gap_connection


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def save_gap_event(
    *,
    symbol: str,
    trade_date: str,
    detected_at: str,
    gap_pct: float,
    gap_direction: str,
    previous_close: float | None,
    open_price: float | None,
    last_price: float | None,
    volume: int | None,
    is_shortable: bool | None,
    hard_to_borrow: bool | None,
    source: str,
) -> dict[str, Any]:
    created_at = utc_now_iso()

    with get_gap_connection() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO gap_events (
                symbol,
                trade_date,
                detected_at,
                gap_pct,
                gap_direction,
                previous_close,
                open_price,
                last_price,
                volume,
                is_shortable,
                hard_to_borrow,
                source,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                symbol.upper(),
                trade_date,
                detected_at,
                gap_pct,
                gap_direction,
                previous_close,
                open_price,
                last_price,
                volume,
                int(is_shortable) if is_shortable is not None else None,
                int(hard_to_borrow) if hard_to_borrow is not None else None,
                source,
                created_at,
            ),
        )

        row = conn.execute(
            """
            SELECT *
            FROM gap_events
            WHERE symbol = ?
              AND trade_date = ?
            """,
            (symbol.upper(), trade_date),
        ).fetchone()

    return dict(row) if row else {}


def get_gap_event(
    symbol: str,
    trade_date: str,
) -> dict[str, Any] | None:
    with get_gap_connection() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM gap_events
            WHERE symbol = ?
              AND trade_date = ?
            """,
            (symbol.upper(), trade_date),
        ).fetchone()

    return dict(row) if row else None


def get_gap_event_by_id(
    gap_event_id: int,
) -> dict[str, Any] | None:
    with get_gap_connection() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM gap_events
            WHERE id = ?
            """,
            (gap_event_id,),
        ).fetchone()

    return dict(row) if row else None


def list_gap_events(
    limit: int = 100,
) -> list[dict[str, Any]]:
    with get_gap_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM gap_events
            ORDER BY detected_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def save_gap_outcome(
    *,
    gap_event_id: int,
    filled: bool | None,
    fill_timestamp: str | None,
    minutes_to_fill: float | None,
    max_run_pct: float | None,
    max_drop_pct: float | None,
    close_result_pct: float | None,
) -> dict[str, Any]:
    calculated_at = utc_now_iso()

    with get_gap_connection() as conn:
        conn.execute(
            """
            INSERT INTO gap_outcomes (
                gap_event_id,
                filled,
                fill_timestamp,
                minutes_to_fill,
                max_run_pct,
                max_drop_pct,
                close_result_pct,
                calculated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(gap_event_id) DO UPDATE SET
                filled = excluded.filled,
                fill_timestamp = excluded.fill_timestamp,
                minutes_to_fill = excluded.minutes_to_fill,
                max_run_pct = excluded.max_run_pct,
                max_drop_pct = excluded.max_drop_pct,
                close_result_pct = excluded.close_result_pct,
                calculated_at = excluded.calculated_at
            """,
            (
                gap_event_id,
                int(filled) if filled is not None else None,
                fill_timestamp,
                minutes_to_fill,
                max_run_pct,
                max_drop_pct,
                close_result_pct,
                calculated_at,
            ),
        )

        row = conn.execute(
            """
            SELECT *
            FROM gap_outcomes
            WHERE gap_event_id = ?
            """,
            (gap_event_id,),
        ).fetchone()

    return dict(row) if row else {}


def get_gap_outcome(
    gap_event_id: int,
) -> dict[str, Any] | None:
    with get_gap_connection() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM gap_outcomes
            WHERE gap_event_id = ?
            """,
            (gap_event_id,),
        ).fetchone()

    return dict(row) if row else None


def count_prior_gap_events(
    symbol: str,
    trade_date: str,
    minimum_gap_pct: float = 2.0,
    lookback_days: int | None = 365,
) -> int:
    cutoff_date = None

    if lookback_days:
        trade_day = datetime.fromisoformat(trade_date).date()
        cutoff_date = (trade_day - timedelta(days=lookback_days)).isoformat()

    with get_gap_connection() as conn:
        row = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM gap_events
            WHERE symbol = ?
              AND trade_date < ?
              AND (? IS NULL OR trade_date >= ?)
              AND ABS(gap_pct) >= ?
            """,
            (
                symbol.upper(),
                trade_date,
                cutoff_date,
                cutoff_date,
                minimum_gap_pct,
            ),
        ).fetchone()

    return row["count"] if row else 0


def count_prior_gap_events_by_direction(
    symbol: str,
    trade_date: str,
    minimum_gap_pct: float = 2.0,
    lookback_days: int | None = 365,
) -> dict[str, int]:
    cutoff_date = None

    if lookback_days:
        trade_day = datetime.fromisoformat(trade_date).date()
        cutoff_date = (trade_day - timedelta(days=lookback_days)).isoformat()

    with get_gap_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                gap_direction,
                COUNT(*) AS count
            FROM gap_events
            WHERE symbol = ?
              AND trade_date < ?
              AND (? IS NULL OR trade_date >= ?)
              AND ABS(gap_pct) >= ?
            GROUP BY gap_direction
            """,
            (
                symbol.upper(),
                trade_date,
                cutoff_date,
                cutoff_date,
                minimum_gap_pct,
            ),
        ).fetchall()

    result = {
        "up": 0,
        "down": 0,
    }

    for row in rows:
        direction = row["gap_direction"]

        if direction in result:
            result[direction] = row["count"]

    return result
