from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from jinja2 import FileSystemLoader

from app.gappers.service import get_live_gappers, get_gap_event_detail


router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"
SHARED_TEMPLATE_DIR = BASE_DIR.parent / "web" / "templates"

templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

templates.env.loader = FileSystemLoader([
    str(TEMPLATE_DIR),
    str(SHARED_TEMPLATE_DIR),
])


@router.get("/api/gappers")
def gappers_api(
    minimum_gap_pct: float = 2.0,
    limit: int | None = None,
):
    return get_live_gappers(
        minimum_gap_pct=minimum_gap_pct,
        limit=limit,
    )


@router.get("/gappers")
def gappers_page(
    request: Request,
):
    return templates.TemplateResponse(
        request,
        "gappers.html",
        {
            "request": request,
        },
    )






@router.get("/api/gappers/{symbol}/daily-history-status")
def daily_history_status_api(
    symbol: str,
    lookback_days: int = 365,
):
    return get_daily_history_status(
        symbol=symbol,
        lookback_days=lookback_days,
    )


@router.get("/api/gappers/{symbol}/daily-history-import-plan")
def daily_history_import_plan_api(
    symbol: str,
    lookback_days: int = 365,
):
    return build_daily_history_import_plan(
        symbol=symbol,
        lookback_days=lookback_days,
    )


@router.post("/api/gappers/{symbol}/import-daily-history")
def import_daily_history_api(
    symbol: str,
    lookback_days: int = 365,
):
    return import_missing_daily_history(
        symbol=symbol,
        lookback_days=lookback_days,
    )




@router.get("/api/gappers/{symbol}/research")
def gap_research_api(
    symbol: str,
    start_date: str,
    end_date: str,
    minimum_gap_pct: float = 2.0,
    target_gap_pct: float | None = None,
):
    return calculate_gap_research_v2(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        minimum_gap_pct=minimum_gap_pct,
        target_gap_pct=target_gap_pct,
    )


@router.get("/api/gappers/{symbol}/{trade_date}")
def gap_detail_api(
    symbol: str,
    trade_date: str,
    minimum_gap_pct: float = 2.0,
    research_lookback_days: int = 365,
):
    return get_gap_event_detail(
        symbol=symbol,
        trade_date=trade_date,
        minimum_gap_pct=minimum_gap_pct,
        research_lookback_days=research_lookback_days,
    )


@router.get("/gappers/{symbol}/{trade_date}")
def gap_detail_page(
    request: Request,
    symbol: str,
    trade_date: str,
):
    detail = get_gap_event_detail(
        symbol=symbol,
        trade_date=trade_date,
    )

    return templates.TemplateResponse(
        request,
        "gap_detail.html",
        {
            "request": request,
            "detail": detail,
        },
    )


from app.gappers.historical_gap_service import (
    get_daily_history_status,
    build_daily_history_import_plan,
    import_missing_daily_history,
)


from app.gappers.research_service import (
    calculate_gap_research_v2,
)
