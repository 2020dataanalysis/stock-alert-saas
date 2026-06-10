from app.gappers.historical_gap_service import (
    discover_historical_gaps,
)
from app.gappers.outcome_service import (
    calculate_daily_gap_outcome,
)
from app.gappers.storage import (
    get_daily_bars,
)


def calculate_statistics(outcomes):
    if not outcomes:
        return {
            "count": 0,
            "fill_rate_pct": 0,
            "avg_max_favorable_pct": 0,
            "avg_max_adverse_pct": 0,
            "avg_close_result_pct": 0,
        }

    count = len(outcomes)

    filled_count = sum(
        1
        for o in outcomes
        if o["filled_same_day"]
    )

    return {
        "count": count,
        "fill_rate_pct": round(
            filled_count / count * 100,
            2,
        ),
        "avg_max_favorable_pct": round(
            sum(
                o["max_favorable_pct"]
                for o in outcomes
            ) / count,
            2,
        ),
        "avg_max_adverse_pct": round(
            sum(
                o["max_adverse_pct"]
                for o in outcomes
            ) / count,
            2,
        ),
        "avg_close_result_pct": round(
            sum(
                o["close_result_pct"]
                for o in outcomes
            ) / count,
            2,
        ),
    }


def calculate_gap_research(
    symbol,
    start_date,
    end_date,
    minimum_gap_pct=2.0,
):
    bars = {
        row["trade_date"]: row
        for row in get_daily_bars(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
        )
    }

    discovery = discover_historical_gaps(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        minimum_gap_pct=minimum_gap_pct,
    )

    outcomes = []

    for gap in discovery["gaps"]:
        row = bars[gap["trade_date"]]

        outcome = calculate_daily_gap_outcome(
            previous_close=gap["previous_close"],
            open_price=row["open_price"],
            high_price=row["high_price"],
            low_price=row["low_price"],
            close_price=row["close_price"],
        )

        outcome["gap_pct"] = gap["gap_pct"]
        outcome["gap_direction"] = gap["gap_direction"]

        outcomes.append(outcome)

    gap_ups = [
        o for o in outcomes
        if o["gap_direction"] == "up"
    ]

    gap_downs = [
        o for o in outcomes
        if o["gap_direction"] == "down"
    ]

    return {
        "symbol": symbol.upper(),
        "all_gaps": calculate_statistics(
            outcomes
        ),
        "gap_ups": calculate_statistics(
            gap_ups
        ),
        "gap_downs": calculate_statistics(
            gap_downs
        ),
    }



def build_gap_research_records(
    symbol,
    start_date,
    end_date,
    minimum_gap_pct=2.0,
):
    bars = {
        row["trade_date"]: row
        for row in get_daily_bars(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
        )
    }

    discovery = discover_historical_gaps(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        minimum_gap_pct=minimum_gap_pct,
    )

    records = []

    for gap in discovery["gaps"]:
        row = bars[gap["trade_date"]]

        outcome = calculate_daily_gap_outcome(
            previous_close=gap["previous_close"],
            open_price=row["open_price"],
            high_price=row["high_price"],
            low_price=row["low_price"],
            close_price=row["close_price"],
        )

        records.append({
            "symbol": symbol.upper(),
            "trade_date": gap["trade_date"],
            "gap_pct": gap["gap_pct"],
            "abs_gap_pct": abs(gap["gap_pct"]),
            "gap_direction": gap["gap_direction"],
            **outcome,
        })

    return records


def filter_direction(
    records,
    direction,
):
    return [
        record
        for record in records
        if record["gap_direction"] == direction
    ]


def filter_gap_size(
    records,
    min_gap_pct,
    max_gap_pct=None,
):
    filtered = [
        record
        for record in records
        if record["abs_gap_pct"] >= min_gap_pct
    ]

    if max_gap_pct is not None:
        filtered = [
            record
            for record in filtered
            if record["abs_gap_pct"] < max_gap_pct
        ]

    return filtered


def filter_comparable_gaps(
    records,
    target_gap_pct,
    tolerance_pct,
):
    target_abs_gap_pct = abs(
        target_gap_pct
    )

    min_gap_pct = max(
        0,
        target_abs_gap_pct - tolerance_pct,
    )

    max_gap_pct = (
        target_abs_gap_pct
        + tolerance_pct
    )

    return [
        record
        for record in records
        if record["abs_gap_pct"] >= min_gap_pct
        and record["abs_gap_pct"] <= max_gap_pct
    ]


def calculate_gap_size_bucket_statistics(
    records,
):
    return {
        "1_to_2": calculate_statistics(
            filter_gap_size(
                records,
                1.0,
                2.0,
            )
        ),
        "2_to_3": calculate_statistics(
            filter_gap_size(
                records,
                2.0,
                3.0,
            )
        ),
        "3_to_4": calculate_statistics(
            filter_gap_size(
                records,
                3.0,
                4.0,
            )
        ),
        "4_to_5": calculate_statistics(
            filter_gap_size(
                records,
                4.0,
                5.0,
            )
        ),
        "5_to_7": calculate_statistics(
            filter_gap_size(
                records,
                5.0,
                7.0,
            )
        ),
        "7_to_10": calculate_statistics(
            filter_gap_size(
                records,
                7.0,
                10.0,
            )
        ),
        "10_plus": calculate_statistics(
            filter_gap_size(
                records,
                10.0,
                None,
            )
        ),
    }


def calculate_comparable_gap_statistics(
    records,
    target_gap_pct,
):
    return {
        "target_gap_pct": target_gap_pct,
        "plus_minus_1_pct": calculate_statistics(
            filter_comparable_gaps(
                records,
                target_gap_pct,
                1.0,
            )
        ),
        "plus_minus_2_pct": calculate_statistics(
            filter_comparable_gaps(
                records,
                target_gap_pct,
                2.0,
            )
        ),
        "plus_minus_3_pct": calculate_statistics(
            filter_comparable_gaps(
                records,
                target_gap_pct,
                3.0,
            )
        ),
        "all_gaps": calculate_statistics(
            records
        ),
    }


def calculate_gap_research_v2(
    symbol,
    start_date,
    end_date,
    minimum_gap_pct=2.0,
    target_gap_pct=None,
):
    records = build_gap_research_records(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        minimum_gap_pct=minimum_gap_pct,
    )

    result = {
        "symbol": symbol.upper(),
        "record_count": len(records),
        "all_gaps": calculate_statistics(
            records
        ),
        "gap_ups": calculate_statistics(
            filter_direction(
                records,
                "up",
            )
        ),
        "gap_downs": calculate_statistics(
            filter_direction(
                records,
                "down",
            )
        ),
        "gap_size_buckets": calculate_gap_size_bucket_statistics(
            records
        ),
    }

    if target_gap_pct is not None:
        result["comparable_gaps"] = calculate_comparable_gap_statistics(
            records,
            target_gap_pct,
        )

    return result
