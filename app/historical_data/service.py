from app.historical_data.repository import (
    add_minute_outcome,
    create_opening_scenario,
    get_historical_bars,
    get_minute_outcomes,
    get_recent_opening_scenarios,
    init_historical_db,
    upsert_historical_bar,
    get_historical_bar_counts,
)


def initialize_historical_data_module():
    init_historical_db()

    return {
        "status": "ok",
        "message": "Historical data module initialized",
    }


def save_opening_scenario(
    symbol,
    trade_date,
    gap_pct,
    open_price,
    previous_close,
):
    init_historical_db()

    scenario_id = create_opening_scenario(
        symbol=symbol,
        trade_date=trade_date,
        gap_pct=gap_pct,
        open_price=open_price,
        previous_close=previous_close,
    )

    return {
        "status": "ok",
        "scenario_id": scenario_id,
    }


def save_minute_outcome(
    scenario_id,
    minute_number,
    price,
    open_price,
):
    init_historical_db()

    outcome_id = add_minute_outcome(
        scenario_id=scenario_id,
        minute_number=minute_number,
        price=price,
        open_price=open_price,
    )

    return {
        "status": "ok",
        "outcome_id": outcome_id,
    }


def list_recent_opening_scenarios(limit=20):
    init_historical_db()

    scenarios = get_recent_opening_scenarios(
        limit=limit
    )

    return {
        "count": len(scenarios),
        "scenarios": scenarios,
    }


def list_minute_outcomes(
    scenario_id,
):
    init_historical_db()

    outcomes = get_minute_outcomes(
        scenario_id
    )

    return {
        "count": len(outcomes),
        "outcomes": outcomes,
    }


def save_historical_bar(
    symbol,
    timestamp,
    timeframe,
    open_price,
    high_price,
    low_price,
    close_price,
    volume,
):
    init_historical_db()

    bar_id = upsert_historical_bar(
        symbol=symbol.upper(),
        timestamp=timestamp,
        timeframe=timeframe,
        open_price=open_price,
        high_price=high_price,
        low_price=low_price,
        close_price=close_price,
        volume=volume,
    )

    return {
        "status": "ok",
        "bar_id": bar_id,
    }


def list_historical_bars(
    symbol,
    timeframe,
    start_timestamp=None,
    end_timestamp=None,
    limit=500,
):
    init_historical_db()

    bars = get_historical_bars(
        symbol=symbol.upper(),
        timeframe=timeframe,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
        limit=limit,
    )

    return {
        "count": len(bars),
        "bars": bars,
    }


def get_historical_data_health():
    init_historical_db()

    counts = get_historical_bar_counts()

    return {
        "status": "ok",
        "dataset_count": len(counts),
        "datasets": counts,
    }