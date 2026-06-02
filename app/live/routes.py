from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from jinja2 import FileSystemLoader


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
    return templates.TemplateResponse(
        request,
        "live.html",
        {
            "request": request,
        },
    )
