from uuid import UUID

import httpx
import pendulum
from fastapi import APIRouter, Depends, Query
from pydantic import ValidationError as PydanticValidationError

from src.api.dependencies import fetch_from_service, get_event_id, get_http_client
from src.api.exceptions import (
    ExternalServiceUnexpectedError,
    InvalidDateFormatError,
    InvalidDateRangeError,
    ValidationError,
    ValueNotFoundError,
)
from src.api.models import EventData, EventNotFound, EventSummary, EventSummaryList
from src.config.conf_logger import setup_logger

logger = setup_logger(__name__, "api")

router = APIRouter()


@router.get("/", include_in_schema=False)
async def healthcheck():
    logger.info("Called second healthcheck [API router]")
    return {"status": "OK"}


@router.get("/events/{event_id}/summary", response_model=EventSummary)
async def get_summary(
        event_id: UUID = Depends(get_event_id),
        client: httpx.AsyncClient = Depends(get_http_client),
):
    """
    Retrieve and return validated event summaries for the given user within the specified date range.

    Data is fetched from the DB Handler service and validated against the EventSummary model.
    If the date format is invalid or the range is illogical (start > end), a ValidationError is raised.
    If the response structure is invalid or unexpected, an ExternalServiceUnexpectedError is raised.

    Parameters:
    - user_id: User ID (extracted from the request path).
    - start_date: Start of the date range (format: YYYY-MM-DD).
    - end_date: End of the date range (format: YYYY-MM-DD).
    - client: HTTP client used for communication with the DB Handler (injected dependency).

    Returns:
    - An EventSummaryList object wrapping a list of validated EventSummary instances.
    """
    response = await client.get(f"events/{event_id}/summary")
    if response.status_code != 200:
        raise ExternalServiceUnexpectedError(service_name="DB Handler")

    data_json = response.json()
    try:
        data = EventData.model_validate(data_json)
        return EventSummary(summary=data)

    except PydanticValidationError as e:
        try:
            EventNotFound.model_validate(data_json)
            raise ValueNotFoundError(event_id=event_id) from e
        except ValidationError:
            raise ExternalServiceUnexpectedError(
                service_name="DB Handler", original_error=e
            ) from e


@router.get("/users/{user_id}/events/summary", response_model=EventSummaryList)
async def get_user_event_summaries(
    user_id: int,
    start_date: str = Query(..., description="Start of the period, format YYYY-MM-DD"),
    end_date: str = Query(..., description="End of the period, format YYYY-MM-DD"),
    client: httpx.AsyncClient = Depends(get_http_client),
):

    try:
        start = pendulum.parse(start_date, strict=True)
        end = pendulum.parse(end_date, strict=True)
    except Exception as e:
        raise InvalidDateFormatError() from e

    if start > end:
        raise InvalidDateRangeError()

    url = f"users/{user_id}/events/summary"
    params = {"start_date": start.to_date_string(), "end_date": end.to_date_string()}

    data_json = await fetch_from_service(client, url, params=params)

    summaries = [EventSummary.model_validate(item) for item in data_json]
    return EventSummaryList(summaries=summaries)