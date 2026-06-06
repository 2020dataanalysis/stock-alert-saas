# app/web/dashboard.py

import json
from pathlib import Path

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services.status_service import get_status_metrics
from app.services.chart_service import get_recent_quotes
from app.web.api import router as api_router
from app.services.alert_service import get_recent_alerts
from app.services.provider_error_service import get_recent_provider_errors
from app.services.system_event_service import get_recent_system_events
# from app.storage.sqlite_store import clear_alerts, save_system_event
from app.services.market_hours_service import get_market_status
from app.data_adapters.movers_adapter import get_mover_symbols
from fastapi.staticfiles import StaticFiles

from app.storage.sqlite_store import (
    clear_alerts,
    clear_alert_rules,
    save_system_event,
)


from app.services.alert_rule_service import (
    get_alert_rules,
    create_alert_rule,
    create_whale_rule,
    generate_mover_rules,
    set_alert_rule_active,
    delete_alert_rule,
)

from app.services.watchlist_service import get_symbol_source_badge
from app.storage.sqlite_store import market_db_connection
from app.config import load_settings

from app.market_state.web.routes import router as market_state_router

from app.scalp_state.routes import router as scalp_state_router

from app.historical_data.routes import router as historical_data_router
from app.historical_data.replay.routes import router as historical_replay_router
from app.statistics.routes import router as statistics_router

from app.live.routes import router as live_router

import sqlite3

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="app/web/static"),
    name="static",
)

app.mount(
    "/market-state-static",
    StaticFiles(directory="app/market_state/web/static"),
    name="market_state_static",
)

app.mount(
    "/scalp-state-static",
    StaticFiles(directory="app/scalp_state/static"),
    name="scalp_state_static",
)

app.mount(
    "/historical-replay-static",
    StaticFiles(directory="app/historical_data/replay/static"),
    name="historical_replay_static",
)

app.mount(
    "/statistics-static",
    StaticFiles(directory="app/statistics/static"),
    name="statistics_static",
)

app.mount(
    "/live/static",
    StaticFiles(directory="app/live/static"),
    name="live_static",
)

app.include_router(api_router)
app.include_router(market_state_router)
app.include_router(scalp_state_router)
app.include_router(historical_data_router)
app.include_router(historical_replay_router)
app.include_router(statistics_router)
app.include_router(live_router)

templates = Jinja2Templates(directory="app/web/templates")



@app.get("/", response_class=HTMLResponse)
async def overview(request: Request):
    settings = load_settings()



    favorite_symbols = set(
        settings["favorite_symbols"]
    )

    mover_symbols = set()

    if settings["use_movers"]:
        mover_symbols = set(
            get_mover_symbols(
                limit=settings["movers_limit"]
            )
        )



    with market_db_connection() as conn:
        conn.row_factory = sqlite3.Row

        quote_count = conn.execute(
            "SELECT COUNT(*) FROM quotes"
        ).fetchone()[0]

        alert_count = conn.execute(
            "SELECT COUNT(*) FROM alerts"
        ).fetchone()[0]

        quotes = [
            dict(row)
            for row in conn.execute("""
                SELECT symbol, last, volume, timestamp
                FROM quotes
                ORDER BY id DESC
                LIMIT 10
            """).fetchall()
        ]

        alerts = conn.execute("""
            SELECT symbol, price_change_pct, volume_change_pct, timestamp
            FROM alerts
            ORDER BY id DESC
            LIMIT 10
        """).fetchall()

        for q in quotes:
            q["source_badge"] = get_symbol_source_badge(
                q["symbol"],
                favorite_symbols,
                mover_symbols,
            )

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
    poll_seconds: int = Form(...),
):
    settings = load_settings()
    settings["poll_seconds"] = poll_seconds

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
                logs[name] = "".join(lines[-50:])
        except FileNotFoundError:
            logs[name] = "Log file not found."

    provider_errors = get_recent_provider_errors()
    system_events = get_recent_system_events()

    return templates.TemplateResponse(
        request=request,
        name="logs.html",
        context={
            "logs": logs,
            "provider_errors": provider_errors,
            "system_events": system_events,
        },
    )


@app.get("/status", response_class=HTMLResponse)
def status(request: Request):
    metrics = get_status_metrics()
    market = get_market_status()
    metrics.update(market)

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


@app.post("/alerts/clear")
async def clear_alerts_route():
    clear_alerts()

    save_system_event(
        event_type="ALERTS_CLEARED",
        service="web_dashboard",
        status="OK",
        message="User cleared market alert history",
    )

    return RedirectResponse("/alerts", status_code=303)



@app.post("/alert-rules/clear")
async def clear_alert_rules_route():

    clear_alert_rules()

    save_system_event(
        event_type="ALERT_RULES_CLEARED",
        service="web_dashboard",
        status="OK",
        message="User cleared all alert rules",
    )

    return RedirectResponse(
        "/alert-rules",
        status_code=303,
    )



def clear_alert_rules():
    with market_db_connection() as conn:
        conn.execute("DELETE FROM alert_rules")


@app.get("/alert-rules", response_class=HTMLResponse)
async def alert_rules_page(
    request: Request,
    message: str = "",
    message_type: str = "info",
):
    rules = get_alert_rules()
    settings = load_settings()

    return templates.TemplateResponse(
        request=request,
        name="alert_rules.html",
        context={
            "rules": rules,
            "settings": settings,
            "message": message,
            "message_type": message_type,
        },
    )


@app.post("/alert-rules/settings")
async def update_alert_rule_settings(
    favorite_symbols: str = Form(...),
    use_movers: bool = Form(False),
    auto_generate_mover_alerts: bool = Form(False),
    clear_existing_mover_alerts_on_startup: bool = Form(False),
    movers_limit: int = Form(...),
):
    settings = load_settings()

    settings["favorite_symbols"] = [
        s.strip().upper()
        for s in favorite_symbols.split(",")
        if s.strip()
    ]

    settings["use_movers"] = use_movers
    settings["auto_generate_mover_alerts"] = auto_generate_mover_alerts
    settings["clear_existing_mover_alerts_on_startup"] = (
        clear_existing_mover_alerts_on_startup
    )
    settings["movers_limit"] = movers_limit

    path = Path("config/settings.json")
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w") as f:
        json.dump(settings, f, indent=2)

    return RedirectResponse(
        "/alert-rules?message=Alert+settings+saved&message_type=success",
        status_code=303,
    )


@app.post("/alert-rules/create")
async def create_alert_rule_route(
    symbol: str = Form(...),
    rule_type: str = Form("threshold"),
    metric: str = Form("last"),
    operator: str = Form(">"),
    threshold: float = Form(0),
    direction: str = Form("both"),
    price_change_pct: float = Form(1.0),
    price_move_type: str = Form("cents"),
    price_move_cents: float = Form(5),
    volume_change_pct: float = Form(10.0),
    window_size: int = Form(5),
    require_volume_confirmation: bool = Form(False),
    is_active: bool = Form(False),
    auto_disable_on_trigger: bool = Form(False),
):
    if rule_type == "threshold":

        create_alert_rule(
            symbol=symbol,
            metric=metric,
            operator=operator,
            threshold=threshold,
            is_active=is_active,
            auto_disable_on_trigger=auto_disable_on_trigger,
        )

    else:

        if direction == "both":

            create_whale_rule(
                symbol=symbol,
                direction="up",
                price_change_pct=price_change_pct,
                volume_change_pct=volume_change_pct,
                window_size=window_size,
                price_move_type=price_move_type,
                price_move_cents=price_move_cents,
                require_volume_confirmation=require_volume_confirmation,
                is_active=is_active,
                auto_disable_on_trigger=auto_disable_on_trigger,
            )

            create_whale_rule(
                symbol=symbol,
                direction="down",
                price_change_pct=price_change_pct,
                volume_change_pct=volume_change_pct,
                window_size=window_size,
                price_move_type=price_move_type,
                price_move_cents=price_move_cents,
                require_volume_confirmation=require_volume_confirmation,
                is_active=is_active,
                auto_disable_on_trigger=auto_disable_on_trigger,
            )

        else:

            create_whale_rule(
                symbol=symbol,
                direction=direction,
                price_change_pct=price_change_pct,
                volume_change_pct=volume_change_pct,
                window_size=window_size,
                price_move_type=price_move_type,
                price_move_cents=price_move_cents,
                require_volume_confirmation=require_volume_confirmation,
                is_active=is_active,
                auto_disable_on_trigger=auto_disable_on_trigger,
            )

    return RedirectResponse("/alert-rules", status_code=303)


@app.post("/alert-rules/{rule_id}/enable")
async def enable_alert_rule(rule_id: int):
    set_alert_rule_active(rule_id, True)
    return RedirectResponse("/alert-rules", status_code=303)


@app.post("/alert-rules/{rule_id}/disable")
async def disable_alert_rule(rule_id: int):
    set_alert_rule_active(rule_id, False)
    return RedirectResponse("/alert-rules", status_code=303)


@app.post("/alert-rules/{rule_id}/delete")
async def delete_alert_rule_route(rule_id: int):
    delete_alert_rule(rule_id)
    return RedirectResponse("/alert-rules", status_code=303)


@app.post("/alert-rules/generate-movers")
async def generate_mover_alert_rules():

    movers = get_mover_symbols(limit=10)

    created = generate_mover_rules(movers)

    print(f"Generated {created} mover rules")

    if created == 0:
        return RedirectResponse(
            "/alert-rules?message=No+movers+returned&message_type=warning",
            status_code=303,
        )

    return RedirectResponse(
        f"/alert-rules?message=Generated+{created}+mover+rules&message_type=success",
        status_code=303,
    )    


@app.get("/alerts", response_class=HTMLResponse)
async def alerts_page(request: Request):
    settings = load_settings()
    alerts = get_recent_alerts()

    return templates.TemplateResponse(
        request=request,
        name="alerts.html",
        context={
            "settings": settings,
            "alerts": alerts,
        },
    )


@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return {"status": "ok"}


