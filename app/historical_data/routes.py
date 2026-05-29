from fastapi import APIRouter

from app.historical_data.service import (
    initialize_historical_data_module,
)


router = APIRouter()


@router.get("/api/historical-data/init")
def initialize_historical_data():
    return initialize_historical_data_module()


@router.get("/historical-data")
def historical_data_page():
    return {
        "module": "historical_data",
        "status": "available",
    }
