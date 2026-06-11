"""
On-Demand Market Data API Routes

These routes expose live Schwab-backed data without writing to the
historical database.

This module is intended to expand into:
    - history
    - quotes
    - movers
    - options chains
    - market hours
"""

from fastapi import APIRouter, HTTPException

from app.on_demand_market_data.history_service import (
    fetch_price_history,
)


router = APIRouter()


@router.get("/api/market-data/history/{symbol}")
def market_data_history_api(
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
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )
