from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from src.config.conf_logger import setup_logger
from src.config.config import DB_HANDLER_URL, DEBUG

logger = setup_logger(__name__, "main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup...")
    _http_client_instance = httpx.AsyncClient(base_url=DB_HANDLER_URL, timeout=5.0)
    app.state.http_client = _http_client_instance
    logger.info(f"HTTP client to {DB_HANDLER_URL} configured.")
    logger.info(f"Started with {DEBUG=}")
    try:
        yield  # Separates code before the application starts and after it stops
    finally:
        logger.info("Application shutdown...")
        await _http_client_instance.aclose()
        logger.info("HTTP client closed.")
