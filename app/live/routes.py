from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from jinja2 import FileSystemLoader

from app.config import load_settings
from app.data_adapters.movers_adapter import get_mover_symbols


router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"
SHARED_TEMPLATE_DIR = BASE_DIR.parent / "web" / "templates"

templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

templates.env.loader = FileSystemLoader([
    str(TEMPLATE_DIR),
    str(SHARED_TEMPLATE_DIR),
])


@router.get("/live")
def live_page(
    request: Request,
):
    settings = load_settings()

    favorite_symbols = settings.get(
        "favorite_symbols",
        []
    )

    mover_symbols = []

    if settings.get("use_movers"):
        mover_symbols = get_mover_symbols(
            limit=settings.get("movers_limit", 10)
        )

    return templates.TemplateResponse(
        request,
        "live.html",
        {
            "request": request,
            "favorite_symbols": favorite_symbols,
            "mover_symbols": mover_symbols,
        },
    )
