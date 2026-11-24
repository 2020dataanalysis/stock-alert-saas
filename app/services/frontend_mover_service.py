import logging

from fastapi import HTTPException

from app.services.backend_client import backend_get
from app.storage.sqlite_store import load_mover_symbols


logger = logging.getLogger(__name__)


def get_fresh_mover_symbols(limit=10):
    try:
        result = backend_get(
            "/movers",
            params={"limit": limit},
        )

        if result["symbols"]:
            return result["symbols"]

        logger.warning("No fresh movers returned; using saved snapshot")

    except HTTPException:
        logger.warning("Mover acquisition unavailable; using saved snapshot")

    return load_mover_symbols(limit=limit)
