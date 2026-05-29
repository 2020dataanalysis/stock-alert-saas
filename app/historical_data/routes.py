from fastapi import APIRouter

from app.historical_data.service import (
    initialize_historical_data_module,
    list_historical_bars,
    list_minute_outcomes,
    list_recent_opening_scenarios,
    save_historical_bar,
    save_minute_outcome,
    save_opening_scenario,
)

from app.historical_data.import_service import (
    import_schwab_price_history_response,
)


router = APIRouter()


@router.get("/api/historical-data/init")
def initialize_historical_data():
    return initialize_historical_data_module()


@router.post("/api/historical-data/opening-scenarios")
def create_opening_scenario_api(
    symbol: str,
    trade_date: str,
    gap_pct: float,
    open_price: float,
    previous_close: float,
):
    return save_opening_scenario(
        symbol=symbol.upper(),
        trade_date=trade_date,
        gap_pct=gap_pct,
        open_price=open_price,
        previous_close=previous_close,
    )


@router.post("/api/historical-data/minute-outcomes")
def create_minute_outcome_api(
    scenario_id: int,
    minute_number: int,
    price: float,
    open_price: float,
):
    return save_minute_outcome(
        scenario_id=scenario_id,
        minute_number=minute_number,
        price=price,
        open_price=open_price,
    )


@router.get("/api/historical-data/opening-scenarios")
def recent_opening_scenarios_api(
    limit: int = 20,
):
    return list_recent_opening_scenarios(
        limit=limit
    )


@router.get("/historical-data")
def historical_data_page():
    return {
        "module": "historical_data",
        "status": "available",
    }


@router.get(
    "/api/historical-data/opening-scenarios/{scenario_id}/outcomes"
)
def scenario_outcomes_api(
    scenario_id: int,
):
    return list_minute_outcomes(
        scenario_id
    )



@router.post("/api/historical-data/bars")
def create_historical_bar_api(
    symbol: str,
    timestamp: str,
    timeframe: str,
    open_price: float,
    high_price: float,
    low_price: float,
    close_price: float,
    volume: int,
):
    return save_historical_bar(
        symbol=symbol,
        timestamp=timestamp,
        timeframe=timeframe,
        open_price=open_price,
        high_price=high_price,
        low_price=low_price,
        close_price=close_price,
        volume=volume,
    )


@router.get("/api/historical-data/bars")
def historical_bars_api(
    symbol: str,
    timeframe: str,
    start_timestamp: str | None = None,
    end_timestamp: str | None = None,
    limit: int = 500,
):
    return list_historical_bars(
        symbol=symbol,
        timeframe=timeframe,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
        limit=limit,
    )


@router.post("/api/historical-data/import/schwab-price-history")
def import_schwab_price_history_api(
    payload: dict,
    frequency_type: str = "minute",
    frequency: int = 1,
):
    return import_schwab_price_history_response(
        response_data=payload,
        frequency_type=frequency_type,
        frequency=frequency,
    )