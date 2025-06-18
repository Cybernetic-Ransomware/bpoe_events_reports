from collections.abc import AsyncGenerator

import httpx

from src.api.exceptions import (
    ExternalServiceConnectionError,
    ExternalServiceNotFoundError,
    ExternalServiceUnexpectedError,
)
from src.config.config import DB_HANDLER_URL


async def get_http_client() -> AsyncGenerator[httpx.AsyncClient]:
    async with httpx.AsyncClient(base_url=DB_HANDLER_URL, timeout=5.0) as client:
        yield client

async def fetch_from_service(client: httpx.AsyncClient, url: str, params: dict | None = None):
    try:
        response = await client.get(url, params=params)
        print("Request URL:", response.request.url, flush=True)
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise ExternalServiceNotFoundError(
                resource_name="resource",
                resource_id=url,
                service_name="DB Handler",
            ) from e
        else:
            raise ExternalServiceUnexpectedError(
                service_name="DB Handler",
                original_error=e,
            ) from e
    except httpx.RequestError as e:
        raise ExternalServiceConnectionError(
            service_name="DB Handler",
            original_error=e,
        ) from e

    try:
        return response.json()
    except Exception as e:
        raise ExternalServiceUnexpectedError(
            service_name="DB Handler",
            original_error=e,
        ) from e
