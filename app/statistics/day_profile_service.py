from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.storage.sqlite_store import get_connection


DEFAULT_WINDOWS = [1, 2, 3, 4, 5, 10, 20, 30, 40, 50, 100, 200, 500, 1000]


@dataclass
class CleanQuote:
    timestamp: str
    last: float
    volume: int


def _fetch_quotes(symbol: str, trade_date: str) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT timestamp, last, volume
            FROM quotes
            WHERE symbol = ?
              AND DATE(timestamp) = ?
              AND last IS NOT NULL
            ORDER BY timestamp ASC
            """,
            (symbol.upper(), trade_date),
        ).fetchall()

    return [
        {
            "timestamp": row[0],
            "last": row[1],
            "volume": row[2],
        }
        for row in rows
    ]


def _clean_quotes(
    rows: list[dict[str, Any]],
    bad_tick_pct_threshold: float = 5.0,
    local_window_size: int = 5,
) -> tuple[list[CleanQuote], list[dict[str, Any]]]:
    clean: list[CleanQuote] = []
    bad_ticks: list[dict[str, Any]] = []

    def local_reference_price(index: int) -> float | None:
        nearby_prices: list[float] = []

        start = max(0, index - local_window_size)
        end = min(len(rows), index + local_window_size + 1)

        for nearby_index in range(start, end):
            if nearby_index == index:
                continue

            nearby_price = rows[nearby_index].get("last")

            if nearby_price is not None:
                nearby_prices.append(float(nearby_price))

        if not nearby_prices:
            return None

        nearby_prices.sort()
        middle = len(nearby_prices) // 2

        if len(nearby_prices) % 2:
            return nearby_prices[middle]

        return (nearby_prices[middle - 1] + nearby_prices[middle]) / 2.0

    for index, row in enumerate(rows):
        last = float(row["last"])
        volume = int(row["volume"] or 0)
        timestamp = row["timestamp"]

        reference_price = local_reference_price(index)

        if reference_price:
            move_pct = abs(last - reference_price) * 100.0 / reference_price

            if move_pct > bad_tick_pct_threshold:
                bad_ticks.append(
                    {
                        "timestamp": timestamp,
                        "reference_last": round(reference_price, 4),
                        "last": last,
                        "move_pct": round(move_pct, 4),
                        "reason": "local_median_outlier",
                    }
                )
                continue

        if clean:
            previous_clean = clean[-1].last
            one_quote_move_pct = (
                abs(last - previous_clean) * 100.0 / previous_clean
                if previous_clean
                else 0.0
            )

            if one_quote_move_pct > 0.5:
                bad_ticks.append(
                    {
                        "timestamp": timestamp,
                        "previous_clean_last": round(previous_clean, 4),
                        "last": last,
                        "move_pct": round(one_quote_move_pct, 4),
                        "reason": "one_quote_jump_outlier",
                    }
                )
                continue

        clean.append(CleanQuote(timestamp=timestamp, last=last, volume=volume))

    return clean, bad_ticks


def _range_stats(quotes: list[CleanQuote]) -> dict[str, Any]:
    if not quotes:
        return {}

    prices = [q.last for q in quotes]
    low = min(prices)
    high = max(prices)
    first = quotes[0].last
    last = quotes[-1].last

    return {
        "open": round(first, 4),
        "high": round(high, 4),
        "low": round(low, 4),
        "close": round(last, 4),
        "range_dollars": round(high - low, 4),
        "range_pct": round((high - low) * 100.0 / low, 4) if low else 0,
        "close_change_dollars": round(last - first, 4),
        "close_change_pct": round((last - first) * 100.0 / first, 4) if first else 0,
    }


def _largest_move_windows(
    quotes: list[CleanQuote],
    windows: list[int] | None = None,
) -> list[dict[str, Any]]:
    if windows is None:
        windows = DEFAULT_WINDOWS

    results: list[dict[str, Any]] = []

    for window in windows:
        if len(quotes) <= window:
            continue

        best_up: dict[str, Any] | None = None
        best_down: dict[str, Any] | None = None

        for i in range(0, len(quotes) - window):
            start = quotes[i]
            end = quotes[i + window]

            move = end.last - start.last
            move_pct = move * 100.0 / start.last if start.last else 0

            candidate = {
                "window": window,
                "start_time": start.timestamp,
                "end_time": end.timestamp,
                "from_price": round(start.last, 4),
                "to_price": round(end.last, 4),
                "move_dollars": round(move, 4),
                "move_pct": round(move_pct, 4),
            }

            if best_up is None or move_pct > best_up["move_pct"]:
                best_up = candidate

            if best_down is None or move_pct < best_down["move_pct"]:
                best_down = candidate

        results.append(
            {
                "window": window,
                "largest_up": best_up,
                "largest_down": best_down,
            }
        )

    if len(quotes) >= 2:
        first = quotes[0]
        last = quotes[-1]
        move = last.last - first.last
        move_pct = move * 100.0 / first.last if first.last else 0

        results.append(
            {
                "window": "entire_day",
                "largest_up": {
                    "window": "entire_day",
                    "start_time": first.timestamp,
                    "end_time": last.timestamp,
                    "from_price": round(first.last, 4),
                    "to_price": round(last.last, 4),
                    "move_dollars": round(move, 4),
                    "move_pct": round(move_pct, 4),
                },
                "largest_down": {
                    "window": "entire_day",
                    "start_time": first.timestamp,
                    "end_time": last.timestamp,
                    "from_price": round(first.last, 4),
                    "to_price": round(last.last, 4),
                    "move_dollars": round(move, 4),
                    "move_pct": round(move_pct, 4),
                },
            }
        )

    return results


def _volume_stats(quotes: list[CleanQuote]) -> dict[str, Any]:
    if len(quotes) < 2:
        return {}

    deltas: list[int] = []

    for i in range(1, len(quotes)):
        delta = quotes[i].volume - quotes[i - 1].volume
        if delta >= 0:
            deltas.append(delta)

    if not deltas:
        return {}

    sorted_deltas = sorted(deltas)

    def percentile(pct: float) -> int:
        idx = int((len(sorted_deltas) - 1) * pct)
        return sorted_deltas[idx]

    max_delta = max(deltas)
    max_index = deltas.index(max_delta) + 1

    return {
        "starting_volume": quotes[0].volume,
        "ending_volume": quotes[-1].volume,
        "total_volume_change": quotes[-1].volume - quotes[0].volume,
        "avg_delta": round(sum(deltas) / len(deltas), 2),
        "max_delta": max_delta,
        "max_delta_time": quotes[max_index].timestamp,
        "p50_delta": percentile(0.50),
        "p90_delta": percentile(0.90),
        "p95_delta": percentile(0.95),
    }


def _fetch_previous_day_stats(symbol: str, trade_date: str) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                DATE(timestamp) AS trade_date,
                MIN(last) AS low,
                MAX(last) AS high,
                MIN(timestamp) AS first_timestamp,
                MAX(timestamp) AS last_timestamp
            FROM quotes
            WHERE symbol = ?
              AND DATE(timestamp) < ?
              AND last IS NOT NULL
            GROUP BY DATE(timestamp)
            ORDER BY DATE(timestamp) DESC
            LIMIT 1
            """,
            (symbol.upper(), trade_date),
        ).fetchone()

    if not row:
        return None

    return {
        "trade_date": row[0],
        "low": row[1],
        "high": row[2],
        "first_timestamp": row[3],
        "last_timestamp": row[4],
    }


def _prior_day_context(symbol: str, trade_date: str, current_range: dict[str, Any]) -> dict[str, Any]:
    previous = _fetch_previous_day_stats(symbol, trade_date)

    if not previous or not current_range:
        return {
            "previous_trade_date": None,
            "inside_day": None,
            "outside_day": None,
            "broke_previous_high": None,
            "broke_previous_low": None,
        }

    today_high = current_range["high"]
    today_low = current_range["low"]
    prev_high = float(previous["high"])
    prev_low = float(previous["low"])

    return {
        "previous_trade_date": previous["trade_date"],
        "previous_high": round(prev_high, 4),
        "previous_low": round(prev_low, 4),
        "inside_day": today_high < prev_high and today_low > prev_low,
        "outside_day": today_high > prev_high and today_low < prev_low,
        "broke_previous_high": today_high > prev_high,
        "broke_previous_low": today_low < prev_low,
        "distance_above_previous_high": round(today_high - prev_high, 4),
        "distance_below_previous_low": round(today_low - prev_low, 4),
    }


def build_day_profile(symbol: str, trade_date: str) -> dict[str, Any]:
    symbol = symbol.upper()

    raw_rows = _fetch_quotes(symbol, trade_date)
    clean_quotes, bad_ticks = _clean_quotes(raw_rows)

    range_stats = _range_stats(clean_quotes)

    return {
        "symbol": symbol,
        "trade_date": trade_date,
        "raw_quote_count": len(raw_rows),
        "clean_quote_count": len(clean_quotes),
        "bad_tick_count": len(bad_ticks),
        "bad_ticks": bad_ticks,
        "data_quality": {
            "bad_tick_pct_threshold": 5.0,
            "bad_tick_rate_pct": round(len(bad_ticks) * 100.0 / len(raw_rows), 4)
            if raw_rows
            else 0,
        },
        "clean_open_timestamp": clean_quotes[0].timestamp if clean_quotes else None,
        "clean_close_timestamp": clean_quotes[-1].timestamp if clean_quotes else None,
        "range": range_stats,
        "prior_day_context": _prior_day_context(symbol, trade_date, range_stats),
        "largest_move_windows": _largest_move_windows(clean_quotes),
        "volume": _volume_stats(clean_quotes),
    }
