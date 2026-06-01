from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.historical_data.backfill_service import (
    backfill_daily_history,
    backfill_default_watchlist_daily,
    backfill_default_watchlist_intraday,
    backfill_intraday_history,
)

from app.historical_data.gap_analysis_service import (
    calculate_gap_bucket_statistics,
    calculate_gap_days,
)

from app.historical_data.gap_opening_summary_service import (
    calculate_gap_opening_pattern_summary,
)

from app.historical_data.import_service import (
    import_live_schwab_price_history,
    import_schwab_price_history_response,
)

from app.historical_data.opening_pattern_service import (
    calculate_opening_patterns,
)

from app.historical_data.service import (
    get_historical_data_health,
    initialize_historical_data_module,
    list_historical_bars,
    list_minute_outcomes,
    list_recent_opening_scenarios,
    save_historical_bar,
    save_minute_outcome,
    save_opening_scenario,
)

from app.historical_data.statistics_service import (
    calculate_daily_opening_summary,
)

from app.historical_data.watchlist_gap_service import (
    calculate_watchlist_gap_statistics,
)

from app.historical_data.watchlist_gap_opening_service import (
    calculate_watchlist_gap_opening_summary,
)



from app.historical_data.replay_catalog_service import (
    get_replay_catalog,
)


from app.historical_data.replay_service import (
    get_replay_summary,
)



from app.historical_data.replay_quote_service import (
    get_replay_quotes,
)


from app.historical_data.replay_date_service import (
    get_replay_dates,
)


from fastapi import Request
from fastapi.templating import Jinja2Templates
from jinja2 import FileSystemLoader
from pathlib import Path


router = APIRouter()


BASE_DIR = Path(__file__).resolve().parent

TEMPLATE_DIR = (
    BASE_DIR / "templates"
)

SHARED_TEMPLATE_DIR = (
    BASE_DIR.parent / "web" / "templates"
)

templates = Jinja2Templates(
    directory=str(TEMPLATE_DIR)
)

templates.env.loader = FileSystemLoader([
    str(TEMPLATE_DIR),
    str(SHARED_TEMPLATE_DIR),
])



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
def historical_data_page(
    request: Request,
):
    return templates.TemplateResponse(
        request,
        "historical_data.html",
        {
            "request": request,
        },
    )


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



@router.post("/api/historical-data/import/live-schwab-price-history")
def import_live_schwab_price_history_api(
    symbol: str,
    period_type: str = "day",
    period: int = 10,
    frequency_type: str = "minute",
    frequency: int = 1,
    need_extended_hours_data: bool = True,
    need_previous_close: bool = True,
):
    return import_live_schwab_price_history(
        symbol=symbol,
        period_type=period_type,
        period=period,
        frequency_type=frequency_type,
        frequency=frequency,
        need_extended_hours_data=need_extended_hours_data,
        need_previous_close=need_previous_close,
    )



@router.get("/historical-data/import", response_class=HTMLResponse)
def historical_data_import_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Historical Data Import</title>
    </head>
    <body>
        <h1>Historical Data Import</h1>

        <p>Use this endpoint:</p>

        <pre>
curl -X POST "http://127.0.0.1:8000/api/historical-data/import/live-schwab-price-history?symbol=TSLA&period_type=day&period=1&frequency_type=minute&frequency=1" | jq
        </pre>
    </body>
    </html>
    """


@router.get("/api/historical-data/statistics/opening-summary")
def opening_summary_api(
    symbol: str,
    lookback_limit: int = 5000,
):
    return calculate_daily_opening_summary(
        symbol=symbol,
        lookback_limit=lookback_limit,
    )


@router.post("/api/historical-data/backfill/intraday")
def backfill_intraday_api(
    symbols: str,
    period: int = 10,
    frequency: int = 1,
):
    symbol_list = [
        symbol.strip().upper()
        for symbol in symbols.split(",")
        if symbol.strip()
    ]

    return backfill_intraday_history(
        symbols=symbol_list,
        period=period,
        frequency=frequency,
    )


@router.get("/api/historical-data/gaps")
def gap_days_api(
    symbol: str,
    limit: int = 500,
):
    return calculate_gap_days(
        symbol=symbol,
        limit=limit,
    )


@router.get("/api/historical-data/gaps/statistics")
def gap_bucket_statistics_api(
    symbol: str,
    bucket_lower: float,
    bucket_upper: float,
    limit: int = 500,
):
    return calculate_gap_bucket_statistics(
        symbol=symbol,
        bucket_lower=bucket_lower,
        bucket_upper=bucket_upper,
        limit=limit,
    )

@router.get("/api/historical-data/opening-patterns")
def opening_patterns_api(
    symbol: str,
    opening_minutes: int = 30,
    limit: int = 20000,
):
    return calculate_opening_patterns(
        symbol=symbol,
        opening_minutes=opening_minutes,
        limit=limit,
    )

@router.get("/api/historical-data/gaps/opening-summary")
def gap_opening_summary_api(
    symbol: str,
    bucket_lower: float,
    bucket_upper: float,
    opening_minutes: int = 30,
    limit: int = 500,
):
    return calculate_gap_opening_pattern_summary(
        symbol=symbol,
        bucket_lower=bucket_lower,
        bucket_upper=bucket_upper,
        opening_minutes=opening_minutes,
        limit=limit,
    )


@router.post("/api/historical-data/backfill/watchlist")
def backfill_watchlist_api(
    period: int = 10,
    frequency: int = 1,
):
    return backfill_default_watchlist_intraday(
        period=period,
        frequency=frequency,
    )

@router.get("/api/historical-data/health")
def historical_data_health_api():
    return get_historical_data_health()


@router.post("/api/historical-data/backfill/daily")
def backfill_daily_api(
    symbols: str,
    period: int = 1,
):
    symbol_list = [
        symbol.strip().upper()
        for symbol in symbols.split(",")
        if symbol.strip()
    ]

    return backfill_daily_history(
        symbols=symbol_list,
        period=period,
    )


@router.post("/api/historical-data/backfill/watchlist-daily")
def backfill_watchlist_daily_api(
    period: int = 1,
):
    return backfill_default_watchlist_daily(
        period=period,
    )

@router.get("/api/historical-data/watchlist/gaps/statistics")
def watchlist_gap_statistics_api(
    bucket_lower: float,
    bucket_upper: float,
    limit: int = 500,
):
    return calculate_watchlist_gap_statistics(
        bucket_lower=bucket_lower,
        bucket_upper=bucket_upper,
        limit=limit,
    )

@router.get("/api/historical-data/watchlist/gaps/opening-summary")
def watchlist_gap_opening_summary_api(
    bucket_lower: float,
    bucket_upper: float,
    opening_minutes: int = 30,
    limit: int = 500,
):
    return calculate_watchlist_gap_opening_summary(
        bucket_lower=bucket_lower,
        bucket_upper=bucket_upper,
        opening_minutes=opening_minutes,
        limit=limit,
    )



@router.get("/api/replay/catalog")
def replay_catalog_api():
    return get_replay_catalog()




@router.get("/historical-data/replay-catalog")
def replay_catalog_page(
    request: Request,
):
    return templates.TemplateResponse(
        request,
        "replay_catalog.html",
        {
            "request": request,
        },
    )


@router.get("/statistics")
def statistics_page(
    request: Request,
):
    return templates.TemplateResponse(
        request,
        "historical_data.html",
        {
            "request": request,
        },
    )



@router.get("/historical-data/replay")
def replay_page(
    request: Request,
):
    return templates.TemplateResponse(
        request,
        "replay.html",
        {
            "request": request,
        },
    )


@router.get("/api/replay/summary")
def replay_summary_api(
    symbol: str,
):
    return get_replay_summary(
        symbol=symbol,
    )


@router.get("/api/replay/quotes")
def replay_quotes_api(
    symbol: str,
    limit: int = 10000,
):
    return get_replay_quotes(
        symbol=symbol,
        limit=limit,
    )


@router.get("/api/replay/dates")
def replay_dates_api(
    symbol: str,
):
    return get_replay_dates(
        symbol=symbol,
    )