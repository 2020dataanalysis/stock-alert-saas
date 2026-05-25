from pathlib import Path

from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates

from app.market_state.replay_service import replay_quotes


BASE_DIR = Path(__file__).resolve().parent

TEMPLATE_DIR = (
    BASE_DIR / "templates"
)


router = APIRouter()

templates = Jinja2Templates(
    directory=str(TEMPLATE_DIR)
)


@router.get("/market-state")
def market_state_page(
    request: Request,
    symbol: str = "TSLA",
    date: str = "2026-05-22"
):

    results = replay_quotes(
        symbol=symbol,
        date=date,
        persist_events=False,
        persist_snapshots=False
    )

    return templates.TemplateResponse(
        request=request,
        name="market_state.html",
        context={
            "results": results[-200:]
        }
    )


@router.get("/api/market-state/replay")
def replay_market_state(
    symbol: str = "TSLA",
    date: str = "2026-05-22"
):

    results = replay_quotes(
        symbol=symbol,
        date=date,
        persist_events=False,
        persist_snapshots=False
    )

    return {
        "symbol": symbol,
        "date": date,
        "count": len(results),
        "results": results[-200:]
    }
