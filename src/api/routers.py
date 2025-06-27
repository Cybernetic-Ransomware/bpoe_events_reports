from uuid import UUID

import httpx
import pendulum
from fastapi import APIRouter, Depends, Query
from pydantic import ValidationError as PydanticValidationError

from src.api.dependencies import fetch_from_service, get_event_id, get_http_client
from src.api.exceptions import ExternalServiceUnexpectedError, ValidationError, ValueNotFoundError
from src.api.models import EventData, EventNotFound, EventSummary
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

    :param event_id:
    :param client:
    :return:
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


@router.get("/users/{user_id}/events/summary")
async def get_user_event_summaries(
    user_id: int,
    start_date: str = Query(..., description="Start of the period, format YYYY-MM-DD"),
    end_date: str = Query(..., description="End of the period, format YYYY-MM-DD"),
    client: httpx.AsyncClient = Depends(get_http_client),
):
    try:
        start = pendulum.parse(start_date, strict=True)
        end = pendulum.parse(end_date, strict=True)
    except Exception:
        raise ValidationError("Invalid date format. Expected format: YYYY-MM-DD") from None

    if start > end:
        raise ValidationError("start_date must be earlier than or equal to end_date")

    url = f"users/{user_id}/events/summary"
    params = {"start_date": start.to_date_string(), "end_date": end.to_date_string()}

    data_json = await fetch_from_service(client, url, params=params)

    summaries = [EventSummary.model_validate(item) for item in data_json]
    return {"summaries": summaries}
