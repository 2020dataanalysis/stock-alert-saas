from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from jinja2 import FileSystemLoader

from app.gappers.service import get_live_gappers


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
