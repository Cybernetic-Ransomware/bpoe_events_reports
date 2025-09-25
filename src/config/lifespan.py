from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from src.api.exceptions import CriticalDependencyError
from src.config.conf_logger import setup_logger
from src.config.config import DB_HANDLER_URL, DEBUG, INTERNAL_DIAGNOSTICS_TOKEN

DB_HANDLER_HEALTH_ENDPOINT = "/health"

logger = setup_logger(__name__, "main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup...")

    if not DEBUG:
        try:
            async with httpx.AsyncClient(base_url=DB_HANDLER_URL, timeout=5.0) as client:
                response = await client.get(DB_HANDLER_HEALTH_ENDPOINT)
                response.raise_for_status()
            logger.info(f"Successfully connected to DB Handler. Status: {response.status_code}")
        except Exception as e:
            logger.error(f"Unexpected error during DB Handler startup check: {e}")
            raise CriticalDependencyError(service_name="DB Handler (Production Check)", original_error=e) from e
    else:
        logger.info("DEBUG mode: Skipping DB Handler connection check during startup.")

    logger.info(f"Started with {DEBUG=}")
    if DEBUG:
        logger.info(f"Admin Diagnostic Randomized Token: {INTERNAL_DIAGNOSTICS_TOKEN}")
    yield
    logger.info("Application shutdown...")
