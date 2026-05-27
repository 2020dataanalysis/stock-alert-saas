from pathlib import Path

from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates

from app.scalp_state.service import (
    get_recent_state_transitions,
    get_scalp_state_rows,
)

BASE_DIR = Path(__file__).resolve().parent

TEMPLATE_DIR = (
    BASE_DIR / "templates"
)


router = APIRouter()

templates = Jinja2Templates(
    directory=str(TEMPLATE_DIR)
)


@router.get("/scalp-state")
def scalp_state_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="scalp_state.html",
        context={
            "title": "Scalp State Tool",
            "rows": get_scalp_state_rows(),
            "transitions": get_recent_state_transitions(),
        }
    )


@router.get("/api/scalp-state")
def scalp_state_api():

    return {
        "rows": get_scalp_state_rows()
    }


@router.get("/api/scalp-state/transitions")
def scalp_state_transitions_api():

    return {
        "transitions": get_recent_state_transitions()
    }