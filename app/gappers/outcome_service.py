from typing import Any


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
