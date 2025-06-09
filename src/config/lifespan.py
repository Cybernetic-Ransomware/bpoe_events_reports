from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from src.api.exceptions import CriticalDependencyError
from src.config.conf_logger import setup_logger
from src.config.config import DB_HANDLER_URL, DEBUG

DB_HANDLER_HEALTH_ENDPOINT = "/health"

logger = setup_logger(__name__, "main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup...")
    _http_client_instance = httpx.AsyncClient(base_url=DB_HANDLER_URL, timeout=5.0)

    if not DEBUG:
        try:
            response = await _http_client_instance.get(DB_HANDLER_HEALTH_ENDPOINT)
            response.raise_for_status()
            logger.info(f" Successfully connected to DB Handler. Status: {response.status_code}")
        except Exception as e:
            logger.error(f"Unexpected error during DB Handler startup check: {e}")
            await _http_client_instance.aclose()
            raise CriticalDependencyError(service_name="DB Handler (Production Check)", original_error=e) from e
    else:
        logger.info("DEBUG mode: Skipping DB Handler connection check during startup.")

    app.state.http_client = _http_client_instance
    logger.info(f"HTTP client to {DB_HANDLER_URL} configured.")
    logger.info(f"Started with {DEBUG=}")
    try:
        yield  # Separates code before the application starts and after it stops
    finally:
        logger.info("Application shutdown...")
        if hasattr(app.state, 'http_client') and app.state.http_client is _http_client_instance:
            await _http_client_instance.aclose()
            logger.info("HTTP client closed.")
