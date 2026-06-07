from pathlib import Path

from fastapi import APIRouter

from app.statistics.day_profile_service import build_day_profile
from fastapi import Request
from fastapi.templating import Jinja2Templates
from jinja2 import FileSystemLoader


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


@router.get("/statistics")
def statistics_page(
    request: Request,
):
    return templates.TemplateResponse(
        request,
        "statistics.html",
        {
            "request": request,
        },
    )


@router.get("/api/statistics/day-profile")
def get_day_profile(symbol: str, trade_date: str):
    return build_day_profile(symbol, trade_date)
