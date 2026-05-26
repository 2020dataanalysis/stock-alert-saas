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


def build_hud_summary(results):

    if not results:

        return {
            "state": "NO_DATA",
            "trade_permission": "WAIT",
            "shock_score": 0,
            "trend_score": 0,
            "noise_score": 0,
        }

    latest = results[-1]

    max_shock = max(
        row["features"]["shock_score"]
        for row in results
    )

    max_trend = max(
        row["features"]["trend_score"]
        for row in results
    )

    max_noise = max(
        row["features"]["noise_score"]
        for row in results
    )

    return {
        "state": latest["state"],
        "trade_permission": latest["trade_permission"],
        "shock_score": max_shock,
        "trend_score": max_trend,
        "noise_score": max_noise,
    }


def filter_results(results, filter_mode):

    if filter_mode == "hide_normal":

        return [
            row for row in results
            if row["state"] != "NORMAL"
        ]

    if filter_mode == "block_only":

        return [
            row for row in results
            if row["trade_permission"] == "BLOCK"
        ]

    if filter_mode == "shock_only":

        return [
            row for row in results
            if "SHOCK" in row["state"]
        ]

    return results


@router.get("/market-state")
def market_state_page(
    request: Request,
    symbol: str = "TSLA",
    date: str = "2026-05-22",
    filter_mode: str = "all"
):

    results = replay_quotes(
        symbol=symbol,
        date=date,
        persist_events=False,
        persist_snapshots=False
    )

    visible_results = results[-200:]

    visible_results = filter_results(
        visible_results,
        filter_mode
    )

    hud = build_hud_summary(
        visible_results
    )

    return templates.TemplateResponse(
        request=request,
        name="market_state.html",
        context={
            "results": visible_results,
            "hud": hud,
            "filter_mode": filter_mode,
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
