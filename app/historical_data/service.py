from app.historical_data.repository import (
    init_historical_db,
)


def initialize_historical_data_module():
    init_historical_db()

    return {
        "status": "ok",
        "message": "Historical data module initialized",
    }
