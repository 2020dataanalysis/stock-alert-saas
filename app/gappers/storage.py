from __future__ import annotations

from datetime import datetime, timezone
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
