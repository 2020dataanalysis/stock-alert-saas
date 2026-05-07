# app/web/dashboard.py

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import load_settings


app = FastAPI()
templates = Jinja2Templates(directory="app/web/templates")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    settings = load_settings()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "settings": settings,
        },
    )


@app.post("/settings")
async def update_settings(
    symbols: str = Form(...),
    price_spike_pct: float = Form(...),
    volume_spike_pct: float = Form(...),
    window_size: int = Form(...),
    poll_seconds: int = Form(...),
):
    import json
    from pathlib import Path

    settings = {
        "symbols": [s.strip().upper() for s in symbols.split(",") if s.strip()],
        "price_spike_pct": price_spike_pct,
        "volume_spike_pct": volume_spike_pct,
        "window_size": window_size,
        "poll_seconds": poll_seconds,
    }

    path = Path("config/settings.json")
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w") as f:
        json.dump(settings, f, indent=2)

    return RedirectResponse("/", status_code=303)