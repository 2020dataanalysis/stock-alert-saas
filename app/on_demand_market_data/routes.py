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

import csv
from datetime import datetime
from io import StringIO

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

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
    format: str = "json",
):
    try:
        result = fetch_price_history(
            symbol=symbol,
            days=days,
            start_date=start_date,
            end_date=end_date,
            interval=interval,
            need_extended_hours_data=need_extended_hours_data,
            need_previous_close=need_previous_close,
        )

        if format.lower() == "csv":
            output = StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=[
                    "datetime",
                    "timestamp",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                ],
            )
            writer.writeheader()

            for candle in result["candles"]:
                epoch_ms = candle.get("datetime")

                timestamp = datetime.fromtimestamp(
                    epoch_ms / 1000
                ).astimezone().isoformat()

                writer.writerow({
                    "datetime": epoch_ms,
                    "timestamp": timestamp,
                    "open": candle.get("open"),
                    "high": candle.get("high"),
                    "low": candle.get("low"),
                    "close": candle.get("close"),
                    "volume": candle.get("volume"),
                })

            filename = (
                f"{result['symbol']}_"
                f"{result['request']['request_mode']}_"
                f"{result['interval']}.csv"
            )

            return Response(
                content=output.getvalue(),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                },
            )

        return result
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )
