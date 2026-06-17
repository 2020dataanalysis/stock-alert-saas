from pathlib import Path

from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.templating import Jinja2Templates
from jinja2 import FileSystemLoader

from app.gappers.service import get_live_gappers, get_gap_event_detail
from app.gappers.snapshot_service import (
    save_gap_dashboard_snapshot_if_changed,
    list_gap_dashboard_snapshots,
    get_gap_dashboard_snapshot,
    export_gap_dashboard_snapshots,
)


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
    payload = get_live_gappers(
        minimum_gap_pct=minimum_gap_pct,
        limit=limit,
    )

    snapshot = save_gap_dashboard_snapshot_if_changed(
        page="gappers",
        source_url="/api/gappers",
        snapshot_key=(
            f"gappers:min_gap={minimum_gap_pct}:"
            f"limit={limit or 'default'}"
        ),
        payload=payload,
    )

    payload["snapshot"] = snapshot

    return payload


@router.get("/api/gappers/snapshots")
def gappers_snapshots_api(
    limit: int = 25,
):
    return {
        "snapshots": list_gap_dashboard_snapshots(
            limit=limit,
        )
    }



def _json_download_response(
    *,
    filename: str,
    payload: dict,
) -> Response:
    import json

    return Response(
        content=json.dumps(payload, indent=2, default=str),
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )


@router.get("/api/gappers/snapshots/export")
def gappers_snapshots_export_api(
    limit: int = 100,
):
    payload = export_gap_dashboard_snapshots(
        limit=limit,
    )

    return _json_download_response(
        filename="gappers_snapshots_export.json",
        payload=payload,
    )


@router.get("/api/gappers/snapshots/{snapshot_id}/download")
def gappers_snapshot_download_api(
    snapshot_id: int,
):
    snapshot = get_gap_dashboard_snapshot(
        snapshot_id=snapshot_id,
    )

    if not snapshot:
        raise HTTPException(
            status_code=404,
            detail="Gappers snapshot not found",
        )

    return _json_download_response(
        filename=f"gappers_snapshot_{snapshot_id}.json",
        payload=snapshot,
    )

@router.get("/api/gappers/snapshots/{snapshot_id}")
def gappers_snapshot_detail_api(
    snapshot_id: int,
):
    snapshot = get_gap_dashboard_snapshot(
        snapshot_id=snapshot_id,
    )

    if not snapshot:
        raise HTTPException(
            status_code=404,
            detail="Gappers snapshot not found",
        )

    return snapshot


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






@router.get("/api/gappers/{symbol}/daily-history-status")
def daily_history_status_api(
    symbol: str,
    lookback_days: int = 365,
):
    return get_daily_history_status(
        symbol=symbol,
        lookback_days=lookback_days,
    )


@router.get("/api/gappers/{symbol}/daily-history-import-plan")
def daily_history_import_plan_api(
    symbol: str,
    lookback_days: int = 365,
):
    return build_daily_history_import_plan(
        symbol=symbol,
        lookback_days=lookback_days,
    )


@router.post("/api/gappers/{symbol}/import-daily-history")
def import_daily_history_api(
    symbol: str,
    lookback_days: int = 365,
):
    return import_missing_daily_history(
        symbol=symbol,
        lookback_days=lookback_days,
    )




@router.get("/api/gappers/{symbol}/research")
def gap_research_api(
    symbol: str,
    start_date: str,
    end_date: str,
    minimum_gap_pct: float = 2.0,
    target_gap_pct: float | None = None,
):
    return calculate_gap_research_v2(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        minimum_gap_pct=minimum_gap_pct,
        target_gap_pct=target_gap_pct,
    )


@router.get("/api/gappers/{symbol}/{trade_date}")
def gap_detail_api(
    symbol: str,
    trade_date: str,
    minimum_gap_pct: float = 2.0,
    research_lookback_days: int = 365,
):
    return get_gap_event_detail(
        symbol=symbol,
        trade_date=trade_date,
        minimum_gap_pct=minimum_gap_pct,
        research_lookback_days=research_lookback_days,
    )


@router.get("/gappers/{symbol}/{trade_date}")
def gap_detail_page(
    request: Request,
    symbol: str,
    trade_date: str,
):
    detail = get_gap_event_detail(
        symbol=symbol,
        trade_date=trade_date,
    )

    return templates.TemplateResponse(
        request,
        "gap_detail.html",
        {
            "request": request,
            "detail": detail,
        },
    )


from app.gappers.historical_gap_service import (
    get_daily_history_status,
    build_daily_history_import_plan,
    import_missing_daily_history,
)


from app.gappers.research_service import (
    calculate_gap_research_v2,
)
