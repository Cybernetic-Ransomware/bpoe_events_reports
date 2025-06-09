import httpx
from fastapi import APIRouter, Depends

from src.api.dependencies import get_http_client
from src.api.exceptions import ExternalServiceConnectionError, ExternalServiceNotFoundError, ExternalServiceUnexpectedError
from src.api.models import EventData, EventSummary
from src.config.conf_logger import setup_logger

logger = setup_logger(__name__, "api")

router = APIRouter()


@router.get("/", include_in_schema=False)
async def healthcheck():
    logger.info("Called second healthcheck [API router]")
    return {"status": "OK"}


@router.get("/events/{event_id}/summary", response_model=EventSummary)
async def get_summary(event_id: int, client: httpx.AsyncClient = Depends(get_http_client)) -> EventSummary:
    try:
        response = await client.get(f"/internal/events/{event_id}")
        response.raise_for_status()
        try:
            data_json = response.json()
        except httpx.ConnectError as e:
            logger.error(f"Failed to decode JSON from internal service for event {event_id}: {e}")
            raise ExternalServiceUnexpectedError(service_name="DB Handler", original_error=e) from e

        data = EventData.model_validate(data_json)
        return EventSummary(summary=data)

    except httpx.HTTPStatusError as e:
        logger.warning(
            f"HTTPStatusError from DB Handler for event {event_id}: {e.response.status_code} - {e.response.text}")
        if e.response.status_code == 404:
            raise ExternalServiceNotFoundError(resource_name="event data", resource_id=event_id,
                                               service_name="DB Handler") from e
        else:
            raise ExternalServiceUnexpectedError(
                service_name="DB Handler",
                original_error=e
            ) from e

    except httpx.RequestError as e:
        logger.error(f"RequestError connecting to DB Handler for event {event_id}: {e}")
        raise ExternalServiceConnectionError(service_name="DB Handler", original_error=e) from e