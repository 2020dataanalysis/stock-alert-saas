from fastapi import FastAPI, HTTPException

from schwab_client.exceptions import SchwabAuthError

from app.gappers.service import get_live_gappers


app = FastAPI(title="Stock Alert Backend")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/gappers")
def gappers(
    minimum_gap_pct: float = 2.0,
    limit: int | None = None,
):
    try:
        return get_live_gappers(
            minimum_gap_pct=minimum_gap_pct,
            limit=limit,
        )
    except SchwabAuthError:
        raise HTTPException(
            status_code=503,
            detail="Schwab authentication unavailable",
        ) from None


from app.gappers.historical_gap_service import (
    import_missing_daily_history,
)
from app.gappers.service import get_gap_event_detail


@app.post("/gappers/{symbol}/import-daily-history")
def import_daily_history(
    symbol: str,
    lookback_days: int = 365,
):
    try:
        return import_missing_daily_history(
            symbol=symbol,
            lookback_days=lookback_days,
        )
    except SchwabAuthError:
        raise HTTPException(
            status_code=503,
            detail="Schwab authentication unavailable",
        ) from None


@app.get("/gappers/{symbol}/{trade_date}")
def gap_event_detail(
    symbol: str,
    trade_date: str,
    minimum_gap_pct: float = 2.0,
    research_lookback_days: int = 365,
):
    try:
        return get_gap_event_detail(
            symbol=symbol,
            trade_date=trade_date,
            minimum_gap_pct=minimum_gap_pct,
            research_lookback_days=research_lookback_days,
        )
    except SchwabAuthError:
        raise HTTPException(
            status_code=503,
            detail="Schwab authentication unavailable",
        ) from None


from app.on_demand_market_data.history_service import (
    fetch_price_history,
)


@app.get("/market-data/history/{symbol}")
def market_data_history(
    symbol: str,
    days: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    interval: str = "1m",
    need_extended_hours_data: bool = True,
    need_previous_close: bool = True,
):
    try:
        return fetch_price_history(
            symbol=symbol,
            days=days,
            start_date=start_date,
            end_date=end_date,
            interval=interval,
            need_extended_hours_data=need_extended_hours_data,
            need_previous_close=need_previous_close,
        )
    except SchwabAuthError:
        raise HTTPException(
            status_code=503,
            detail="Schwab authentication unavailable",
        ) from None
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from None


from app.services.token_status_service import get_token_status


@app.get("/token-status")
def token_status():
    return get_token_status()


from app.historical_data.bars.imports.import_service import (
    import_live_schwab_price_history,
)

from app.historical_data.bars.imports.backfill_service import (
    backfill_daily_history,
    backfill_intraday_history,
    backfill_default_watchlist_daily,
    backfill_default_watchlist_intraday,
)


@app.post("/historical-data/import/live-schwab-price-history")
def import_live_history(
    symbol: str,
    period_type: str = "day",
    period: int = 10,
    frequency_type: str = "minute",
    frequency: int = 1,
    need_extended_hours_data: bool = True,
    need_previous_close: bool = True,
):
    return import_live_schwab_price_history(
        symbol=symbol,
        period_type=period_type,
        period=period,
        frequency_type=frequency_type,
        frequency=frequency,
        need_extended_hours_data=need_extended_hours_data,
        need_previous_close=need_previous_close,
    )


@app.post("/historical-data/backfill/intraday")
def backfill_intraday(
    symbols: str,
    period: int = 10,
    frequency: int = 1,
):
    return backfill_intraday_history(
        symbols=[
            symbol.strip().upper()
            for symbol in symbols.split(",")
            if symbol.strip()
        ],
        period=period,
        frequency=frequency,
    )


@app.post("/historical-data/backfill/daily")
def backfill_daily(
    symbols: str,
    period: int = 1,
):
    return backfill_daily_history(
        symbols=[
            symbol.strip().upper()
            for symbol in symbols.split(",")
            if symbol.strip()
        ],
        period=period,
    )


app.add_api_route(
    "/historical-data/backfill/watchlist",
    backfill_default_watchlist_intraday,
    methods=["POST"],
)

app.add_api_route(
    "/historical-data/backfill/watchlist-daily",
    backfill_default_watchlist_daily,
    methods=["POST"],
)


from app.backend.mover_acquisition import acquire_movers


@app.get("/movers")
def movers(limit: int = 10):
    try:
        symbols = acquire_movers(limit=limit)

        return {
            "symbols": symbols,
            "count": len(symbols),
        }

    except SchwabAuthError:
        raise HTTPException(
            status_code=503,
            detail="Schwab authentication unavailable",
        ) from None
