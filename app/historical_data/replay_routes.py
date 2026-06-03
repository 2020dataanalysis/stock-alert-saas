from pathlib import Path

from fastapi import APIRouter
from fastapi import Request
from fastapi.templating import Jinja2Templates
from jinja2 import FileSystemLoader

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
    trade_date: str | None = None,
    limit: int = 10000,
):
    return get_replay_quotes(
        symbol=symbol,
        trade_date=trade_date,
        limit=limit,
    )


@router.get("/api/replay/dates")
def replay_dates_api(
    symbol: str,
):
    return get_replay_dates(
        symbol=symbol,
    )
