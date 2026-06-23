from pathlib import Path
import csv
from io import StringIO

from fastapi import APIRouter
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import Response
from jinja2 import FileSystemLoader

from app.historical_data.replay.catalog_service import (
    get_replay_catalog,
)
from app.historical_data.replay.service import (
    get_replay_summary,
)
from app.historical_data.replay.quote_service import (
    get_replay_quotes,
)
from app.historical_data.replay.date_service import (
    get_replay_dates,
)


router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent

TEMPLATE_DIR = (
    BASE_DIR / "templates"
)

SHARED_TEMPLATE_DIR = (
    BASE_DIR.parent.parent / "web" / "templates"
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
    format: str = "json",
):
    result = get_replay_quotes(
        symbol=symbol,
        trade_date=trade_date,
        limit=limit,
    )

    if format.lower() != "csv":
        return result

    output = StringIO()
    quotes = result.get("quotes", [])

    fieldnames = [
        "symbol",
        "timestamp",
        "last",
        "bid",
        "ask",
        "volume",
        "trade_date",
    ]

    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
        extrasaction="ignore",
    )
    writer.writeheader()

    for quote in quotes:
        row = dict(quote)
        row["symbol"] = result.get("symbol", symbol.upper())
        row["trade_date"] = trade_date or ""
        writer.writerow(row)

    normalized_symbol = symbol.upper().strip()
    date_part = trade_date or "all"

    filename = f"{normalized_symbol}_{date_part}_historical_quotes.csv"

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )


@router.get("/api/replay/dates")
def replay_dates_api(
    symbol: str,
):
    return get_replay_dates(
        symbol=symbol,
    )
