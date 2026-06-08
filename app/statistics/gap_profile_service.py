from __future__ import annotations

from typing import Any

from app.storage.sqlite_store import get_connection
from app.statistics.day_profile_service import build_day_profile


def _fetch_day_open_high_low_close(symbol: str, trade_date: str) -> dict[str, Any] | None:
    symbol = symbol.upper()

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                (
                    SELECT q1.last
                    FROM quotes q1
                    WHERE q1.symbol = ?
                      AND DATE(q1.timestamp) = ?
                      AND q1.last IS NOT NULL
                    ORDER BY q1.timestamp ASC
                    LIMIT 1
                ) AS open,
                MIN(last) AS low,
                MAX(last) AS high,
                (
                    SELECT q2.last
                    FROM quotes q2
                    WHERE q2.symbol = ?
                      AND DATE(q2.timestamp) = ?
                      AND q2.last IS NOT NULL
                    ORDER BY q2.timestamp DESC
                    LIMIT 1
                ) AS close
            FROM quotes
            WHERE symbol = ?
              AND DATE(timestamp) = ?
              AND last IS NOT NULL
            """,
            (symbol, trade_date, symbol, trade_date, symbol, trade_date),
        ).fetchone()

    if not row or row[0] is None:
        return None

    return {
        "open": float(row[0]),
        "low": float(row[1]),
        "high": float(row[2]),
        "close": float(row[3]),
    }


def _fetch_previous_close(symbol: str, trade_date: str) -> dict[str, Any] | None:
    symbol = symbol.upper()

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                DATE(timestamp) AS previous_trade_date,
                (
                    SELECT q2.last
                    FROM quotes q2
                    WHERE q2.symbol = ?
                      AND DATE(q2.timestamp) = DATE(quotes.timestamp)
                      AND q2.last IS NOT NULL
                    ORDER BY q2.timestamp DESC
                    LIMIT 1
                ) AS previous_close
            FROM quotes
            WHERE symbol = ?
              AND DATE(timestamp) < ?
              AND last IS NOT NULL
            GROUP BY DATE(timestamp)
            ORDER BY DATE(timestamp) DESC
            LIMIT 1
            """,
            (symbol, symbol, trade_date),
        ).fetchone()

    if not row or row[1] is None:
        return None

    return {
        "previous_trade_date": row[0],
        "previous_close": float(row[1]),
    }



def _fetch_gap_fill_timestamp(
    symbol: str,
    trade_date: str,
    gap_direction: str,
    fill_level: float,
    include_premarket: bool = False,
    include_regular: bool = True,
    include_after_hours: bool = False,
) -> str | None:
    symbol = symbol.upper()

    if gap_direction == "up":
        condition = "last <= ?"
    elif gap_direction == "down":
        condition = "last >= ?"
    else:
        return None

    session_conditions: list[str] = []

    if include_premarket:
        session_conditions.append("TIME(timestamp) < '13:30:00'")

    if include_regular:
        session_conditions.append(
            "TIME(timestamp) >= '13:30:00' AND TIME(timestamp) <= '20:00:00'"
        )

    if include_after_hours:
        session_conditions.append("TIME(timestamp) > '20:00:00'")

    if not session_conditions:
        return None

    session_sql = " OR ".join(f"({item})" for item in session_conditions)

    with get_connection() as conn:
        row = conn.execute(
            f"""
            SELECT timestamp
            FROM quotes
            WHERE symbol = ?
              AND DATE(timestamp) = ?
              AND last IS NOT NULL
              AND {condition}
              AND ({session_sql})
            ORDER BY timestamp ASC
            LIMIT 1
            """,
            (symbol, trade_date, fill_level),
        ).fetchone()

    if not row:
        return None

    return row[0]


def _minutes_between(start_timestamp: str, end_timestamp: str | None) -> float | None:
    if not start_timestamp or not end_timestamp:
        return None

    from datetime import datetime

    start = datetime.fromisoformat(start_timestamp)
    end = datetime.fromisoformat(end_timestamp)

    return round((end - start).total_seconds() / 60.0, 2)


def _session_baseline_timestamp(
    trade_date: str,
    open_timestamp: str | None,
    include_premarket: bool,
    include_regular: bool,
    include_after_hours: bool,
) -> str | None:
    if include_premarket:
        return open_timestamp

    if include_regular:
        return f"{trade_date}T13:30:00+00:00"

    if include_after_hours:
        return f"{trade_date}T20:00:00+00:00"

    return open_timestamp

def build_gap_profile(
    symbol: str,
    trade_date: str,
    include_premarket: bool = False,
    include_regular: bool = True,
    include_after_hours: bool = False,
) -> dict[str, Any]:
    symbol = symbol.upper()

    profile = build_day_profile(symbol, trade_date)
    day = profile.get("range") or {}
    previous = _fetch_previous_close(symbol, trade_date)

    if not day or not previous:
        return {
            "symbol": symbol,
            "trade_date": trade_date,
            "has_gap_data": False,
        }

    previous_close = previous["previous_close"]
    open_price = day["open"]
    open_timestamp = profile.get("clean_open_timestamp")

    gap_dollars = open_price - previous_close
    gap_pct = gap_dollars * 100.0 / previous_close if previous_close else 0.0

    if gap_pct > 0:
        gap_direction = "up"
        filled = day["low"] <= previous_close
        distance_to_fill_dollars = 0.0 if filled else day["low"] - previous_close
    elif gap_pct < 0:
        gap_direction = "down"
        filled = day["high"] >= previous_close
        distance_to_fill_dollars = 0.0 if filled else previous_close - day["high"]
    else:
        gap_direction = "flat"
        filled = True
        distance_to_fill_dollars = 0.0

    fill_timestamp = (
        _fetch_gap_fill_timestamp(
            symbol,
            trade_date,
            gap_direction,
            previous_close,
            include_premarket=include_premarket,
            include_regular=include_regular,
            include_after_hours=include_after_hours,
        )
        if filled
        else None
    )

    if include_premarket:
        baseline_timestamp = open_timestamp
    elif include_regular:
        baseline_timestamp = f"{trade_date}T13:30:00+00:00"
    elif include_after_hours:
        baseline_timestamp = f"{trade_date}T20:00:00+00:00"
    else:
        baseline_timestamp = open_timestamp

    minutes_to_fill = _minutes_between(
        baseline_timestamp,
        fill_timestamp,
    )

    distance_to_fill_pct = (
        distance_to_fill_dollars * 100.0 / previous_close
        if previous_close
        else 0.0
    )

    return {
        "symbol": symbol,
        "trade_date": trade_date,
        "has_gap_data": True,
        "previous_trade_date": previous["previous_trade_date"],
        "previous_close": round(previous_close, 4),
        "open": round(open_price, 4),
        "high": round(day["high"], 4),
        "low": round(day["low"], 4),
        "close": round(day["close"], 4),
        "gap_dollars": round(gap_dollars, 4),
        "gap_pct": round(gap_pct, 4),
        "gap_direction": gap_direction,
        "fill_level": round(previous_close, 4),
        "filled": filled,
        "sessions": {
            "include_premarket": include_premarket,
            "include_regular": include_regular,
            "include_after_hours": include_after_hours,
        },
        "fill_timestamp": fill_timestamp,
        "fill_baseline_timestamp": baseline_timestamp,
        "minutes_to_fill": minutes_to_fill,
        "distance_to_fill_dollars": round(distance_to_fill_dollars, 4),
        "distance_to_fill_pct": round(distance_to_fill_pct, 4),
    }
