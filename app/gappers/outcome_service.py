from datetime import datetime, time
from typing import Any
from zoneinfo import ZoneInfo

from app.gappers.storage import get_minute_bars


def calculate_daily_gap_outcome(
    previous_close: float,
    open_price: float,
    high_price: float,
    low_price: float,
    close_price: float,
) -> dict[str, Any]:

    gap_direction = (
        "up"
        if open_price >= previous_close
        else "down"
    )

    if gap_direction == "up":
        filled_same_day = (
            low_price <= previous_close
        )

        closest_price = low_price

        closest_distance_pct = (
            abs(low_price - previous_close)
            / previous_close
            * 100
        )

        max_favorable_pct = (
            (high_price - open_price)
            / open_price
            * 100
        )

        max_adverse_pct = (
            (low_price - open_price)
            / open_price
            * 100
        )

    else:
        filled_same_day = (
            high_price >= previous_close
        )

        closest_price = high_price

        closest_distance_pct = (
            abs(high_price - previous_close)
            / previous_close
            * 100
        )

        max_favorable_pct = (
            (open_price - low_price)
            / open_price
            * 100
        )

        max_adverse_pct = (
            (open_price - high_price)
            / open_price
            * 100
        )

    close_result_pct = (
        (close_price - open_price)
        / open_price
        * 100
    )

    return {
        "gap_direction": gap_direction,
        "filled_same_day": filled_same_day,
        "closest_price": round(
            closest_price,
            4,
        ),
        "closest_distance_pct": round(
            closest_distance_pct,
            4,
        ),
        "max_favorable_pct": round(
            max_favorable_pct,
            4,
        ),
        "max_adverse_pct": round(
            max_adverse_pct,
            4,
        ),
        "close_result_pct": round(
            close_result_pct,
            4,
        ),
        "outcome_source": "daily",
    }



def _parse_iso_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _regular_session_bounds_utc(
    trade_date: str,
):
    eastern = ZoneInfo("America/New_York")
    utc = ZoneInfo("UTC")

    session_date = datetime.fromisoformat(
        trade_date
    ).date()

    market_open = datetime.combine(
        session_date,
        time(9, 30),
        tzinfo=eastern,
    ).astimezone(utc)

    market_close = datetime.combine(
        session_date,
        time(16, 0),
        tzinfo=eastern,
    ).astimezone(utc)

    return market_open, market_close


def calculate_minute_gap_fill_timing(
    symbol: str,
    trade_date: str,
    previous_close: float,
    gap_direction: str,
) -> dict[str, Any]:
    bars = get_minute_bars(
        symbol=symbol,
        trade_date=trade_date,
    )

    if not bars:
        return {
            "minute_data_available": False,
            "filled": None,
            "fill_timestamp": None,
            "minutes_to_fill": None,
        }

    market_open, market_close = _regular_session_bounds_utc(
        trade_date
    )

    session_bars = []

    for bar in bars:
        timestamp = _parse_iso_timestamp(
            bar["bar_timestamp"]
        )

        if market_open <= timestamp <= market_close:
            session_bars.append(
                {
                    **bar,
                    "parsed_timestamp": timestamp,
                }
            )

    if not session_bars:
        return {
            "minute_data_available": False,
            "filled": None,
            "fill_timestamp": None,
            "minutes_to_fill": None,
        }

    for bar in session_bars:
        if gap_direction == "up":
            filled = (
                bar["low_price"] is not None
                and bar["low_price"] <= previous_close
            )
        else:
            filled = (
                bar["high_price"] is not None
                and bar["high_price"] >= previous_close
            )

        if filled:
            minutes_to_fill = (
                bar["parsed_timestamp"] - market_open
            ).total_seconds() / 60

            return {
                "minute_data_available": True,
                "filled": True,
                "fill_timestamp": bar["bar_timestamp"],
                "minutes_to_fill": round(
                    minutes_to_fill,
                    2,
                ),
            }

    return {
        "minute_data_available": True,
        "filled": False,
        "fill_timestamp": None,
        "minutes_to_fill": None,
    }
