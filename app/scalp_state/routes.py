from pathlib import Path

from fastapi import APIRouter, Query
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from jinja2 import FileSystemLoader
from jinja2 import FileSystemLoader
from app.scalp_state.service import (
    get_recent_scalp_state_logs,
    get_recent_state_transitions,
    get_scalp_state_rows,
)

BASE_DIR = Path(__file__).resolve().parent

TEMPLATE_DIR = (
    BASE_DIR / "templates"
)


router = APIRouter()

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




def parse_temporary_symbols(temporary_symbols):
    if not temporary_symbols:
        return []

    symbols = []

    for raw_symbol in temporary_symbols.split(","):
        symbol = raw_symbol.strip().upper()

        if not symbol:
            continue

        if not symbol.replace(".", "").replace("-", "").isalnum():
            continue

        symbols.append(symbol)

    return list(dict.fromkeys(symbols))


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
def scalp_state_api(
    temporary_symbols: str = Query(default="")
):

    temporary_symbol_list = parse_temporary_symbols(
        temporary_symbols
    )

    symbols = None

    if temporary_symbol_list:
        symbols = temporary_symbol_list

    return {
        "temporary_symbols": temporary_symbol_list,
        "rows": get_scalp_state_rows(symbols=symbols)
    }


@router.get("/api/scalp-state/transitions")
def scalp_state_transitions_api():

    return {
        "transitions": get_recent_state_transitions()
    }

@router.get("/api/scalp-state/logs")
def scalp_state_logs_api(
    symbol: str = Query(default=""),
    limit: int = Query(default=200)
):

    clean_symbol = symbol.strip().upper() or None

    return {
        "logs": get_recent_scalp_state_logs(
            limit=limit,
            symbol=clean_symbol,
        )
    }


@router.post("/api/scalp-state/logs/clear")
def clear_scalp_state_logs_api():

    from app.scalp_state.database import scalp_state_db_connection

    with scalp_state_db_connection() as conn:
        conn.execute("DELETE FROM scalp_state_log")

    return {
        "ok": True
    }
