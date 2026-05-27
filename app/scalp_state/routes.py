from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates


router = APIRouter()

templates = Jinja2Templates(directory="app/scalp_state/templates")


@router.get("/scalp-state")
def scalp_state_page(request: Request):
    return templates.TemplateResponse(
        "scalp_state.html",
        {
            "request": request,
            "title": "Scalp State Tool",
        },
    )
