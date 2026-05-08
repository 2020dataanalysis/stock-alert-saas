# app/web/dashboard.py

import json
from pathlib import Path

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services.status_service import get_status_metrics
from app.services.chart_service import get_recent_quotes

from app.config import load_settings
import sqlite3

app = FastAPI()
templates = Jinja2Templates(directory="app/web/templates")


@app.get("/", response_class=HTMLResponse)
async def overview(request: Request):
    settings = load_settings()

    conn = sqlite3.connect("data/market_data.db")
    conn.row_factory = sqlite3.Row

    # counts
    quote_count = conn.execute("SELECT COUNT(*) FROM quotes").fetchone()[0]
    alert_count = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]

    # last quotes
    quotes = conn.execute("""
        SELECT symbol, last, volume, timestamp
        FROM quotes
        ORDER BY id DESC
        LIMIT 10
    """).fetchall()

    # last alerts
    alerts = conn.execute("""
        SELECT symbol, price_change_pct, volume_change_pct, timestamp
        FROM alerts
        ORDER BY id DESC
        LIMIT 10
    """).fetchall()

    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="overview.html",
        context={
            "settings": settings,
            "quote_count": quote_count,
            "alert_count": alert_count,
            "quotes": quotes,
            "alerts": alerts,
        },
    )

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    settings = load_settings()

    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context={
            "settings": settings,
        },
    )


@app.post("/settings")
async def update_settings(
    favorite_symbols: str = Form(...),
    use_movers: bool = Form(False),
    movers_limit: int = Form(...),
    price_spike_pct: float = Form(...),
    volume_spike_pct: float = Form(...),
    window_size: int = Form(...),
    poll_seconds: int = Form(...),
):
    settings = {
        "favorite_symbols": [
            s.strip().upper()
            for s in favorite_symbols.split(",")
            if s.strip()
        ],
        "use_movers": use_movers,
        "movers_limit": movers_limit,
        "price_spike_pct": price_spike_pct,
        "volume_spike_pct": volume_spike_pct,
        "window_size": window_size,
        "poll_seconds": poll_seconds,
    }

    path = Path("config/settings.json")
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w") as f:
        json.dump(settings, f, indent=2)

    return RedirectResponse("/settings", status_code=303)



@app.get("/logs", response_class=HTMLResponse)
async def logs_page(request: Request):
    log_files = {
        "debug_log": "logs/debug.log",
        "streamer_out": "logs/streamer.out.log",
        "streamer_err": "logs/streamer.err.log",
    }

    logs = {}

    for name, path in log_files.items():
        try:
            with open(path, "r") as f:
                lines = f.readlines()
                logs[name] = "".join(lines[-100:])
        except FileNotFoundError:
            logs[name] = "Log file not found."

    return templates.TemplateResponse(
        request=request,
        name="logs.html",
        context={
            "logs": logs,
        },
    )


@app.get("/status", response_class=HTMLResponse)
def status(request: Request):
    metrics = get_status_metrics()

    return templates.TemplateResponse(
        request,
        "status.html",
        metrics
    )


@app.get("/charts", response_class=HTMLResponse)
async def charts_page(request: Request):
    settings = load_settings()

    quotes = get_recent_quotes()
    # print("QUOTES SENT TO CHART:", quotes[:5])

    return templates.TemplateResponse(
        request=request,
        name="charts.html",
        context={
            "settings": settings,
            "quotes": quotes,
        },
    )



@app.get("/alerts", response_class=HTMLResponse)
async def alerts_page(request: Request):
    settings = load_settings()

    return templates.TemplateResponse(
        request=request,
        name="alerts.html",
        context={
            "settings": settings,
        },
    )
