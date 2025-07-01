from collections.abc import AsyncGenerator
from typing import Annotated, cast

import httpx
import pendulum
from fastapi import Path, Query

from src.api.examples import summary_event_id_examples
from src.api.exceptions import (
    ExternalServiceConnectionError,
    ExternalServiceNotFoundError,
    ExternalServiceUnexpectedError,
    InvalidDateFormatError,
    InvalidDateRangeError,
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

def get_event_id():
    return Path(
        ...,
        title="Event ID",
        description="Unique identifier for the event",
        openapi_extra={"examples": summary_event_id_examples}
    )

def get_date_range(
    start_date: Annotated[str, Query(..., description="Start datetime in ISO 8601 format, e.g. 2025-07-01T15:00:00")],
    end_date: Annotated[str, Query(..., description="End datetime in ISO 8601 format, e.g. 2025-07-10T18:00:00")],
) -> tuple[pendulum.DateTime, pendulum.DateTime]:

    try:
        start = pendulum.parse(start_date, strict=True)
        end = pendulum.parse(end_date, strict=True)

        start = cast(pendulum.DateTime, start)
        end = cast(pendulum.DateTime, end)

        start = start.in_timezone('UTC')
        end = end.in_timezone('UTC')

    except Exception as e:
        raise InvalidDateFormatError() from e

    if start > end:
        raise InvalidDateRangeError()

    return start, end

