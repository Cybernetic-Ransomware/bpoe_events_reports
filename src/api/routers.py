from uuid import UUID

import httpx
import pendulum
from fastapi import APIRouter, Depends
from pydantic import ValidationError as PydanticValidationError

from src.api.dependencies import fetch_from_service, get_date_range, get_event_id, get_http_client
from src.api.exceptions import (
    ExternalServiceUnexpectedError,
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
    date_range: tuple[pendulum.DateTime, pendulum.DateTime] = Depends(get_date_range),
    client: httpx.AsyncClient = Depends(get_http_client),
):
    """
    Retrieve and return a list of validated event summaries for a given user within a specified date range.

    Data is fetched from the DB Handler service using the provided user ID and date range parameters.
    Each item is validated against the EventSummary model. If the date format is invalid or the range is illogical
    (e.g. start > end), a ValidationError is raised. If the structure of the response is invalid or unexpected,
    an ExternalServiceUnexpectedError is raised.

    Parameters:
    - user_id: ID of the user whose event summaries are to be fetched.
    - date_range: Tuple containing the start and end date as Pendulum DateTime objects.
    - client: HTTP client used for communication with the DB Handler (injected dependency).

    Returns:
    - An EventSummaryList object wrapping a list of validated EventSummary instances.
    """
    start, end = date_range

    url = f"users/{user_id}/events/summary"
    params = {"start_date": start.to_date_string(), "end_date": end.to_date_string()}

    data_json = await fetch_from_service(client, url, params=params)

    summaries = [EventSummary.model_validate(item) for item in data_json]
    return EventSummaryList(summaries=summaries)


@router.get("/events/{event_id}/costs/details")
async def get_event_cost_details(event_id: UUID, client: httpx.AsyncClient = Depends(get_http_client)):
    """Return detailed cost breakdown for a specific event."""
    raise NotImplementedError("Endpoint not implemented yet.")


@router.get("/users/{user_id}/events/financial-summary")
async def get_user_financial_summary(
        user_id: int,
        date_range: tuple[pendulum.DateTime, pendulum.DateTime] = Depends(get_date_range),
        client: httpx.AsyncClient = Depends(get_http_client)
):
    """Return financial summary of user's events in a given date range."""
    start, end = date_range
    raise NotImplementedError("Endpoint not implemented yet.")


@router.get("/events/{event_id}/participants/invited")
async def get_invited_participants(event_id: UUID, client: httpx.AsyncClient = Depends(get_http_client)):
    """Return a list of participants invited to an event."""
    raise NotImplementedError("Endpoint not implemented yet.")


@router.get("/events/{event_id}/participants/accepted")
async def get_accepted_participants(event_id: UUID, client: httpx.AsyncClient = Depends(get_http_client)):
    """Return participants who accepted the invitation and their settlement declarations."""
    raise NotImplementedError("Endpoint not implemented yet.")


@router.get("/events/{event_id}/locations")
async def get_event_locations(event_id: UUID, client: httpx.AsyncClient = Depends(get_http_client)):
    """Return locations and timestamps associated with a specific event."""
    raise NotImplementedError("Endpoint not implemented yet.")


@router.get("/events/{event_id}/participants/settlement-status")
async def get_participant_settlement_status(event_id: UUID, client: httpx.AsyncClient = Depends(get_http_client)):
    """Return participants and their declared settlement shares and status."""
    raise NotImplementedError("Endpoint not implemented yet.")


@router.get("/users/{user_id}/events/owned")
async def get_owned_events(
        user_id: int,
        date_range: tuple[pendulum.DateTime, pendulum.DateTime] = Depends(get_date_range),
        client: httpx.AsyncClient = Depends(get_http_client)
):
    """Return events owned by a user within a date range."""
    raise NotImplementedError("Endpoint not implemented yet.")


@router.get("/users/{user_id}/events/unsettled")
async def get_unsettled_events(
        user_id: int,
        date_range: tuple[pendulum.DateTime, pendulum.DateTime] = Depends(get_date_range),
        client: httpx.AsyncClient = Depends(get_http_client)
):
    """Return events with incomplete settlements for a user."""
    start, end = date_range
    raise NotImplementedError("Endpoint not implemented yet.")


@router.get("/users/{user_id}/balance-details")
async def get_user_balance_details(
        user_id: int,
        date_range: tuple[pendulum.DateTime, pendulum.DateTime] = Depends(get_date_range),
        client: httpx.AsyncClient = Depends(get_http_client)
):
    """Return detailed balance report for the user."""
    start, end = date_range
    raise NotImplementedError("Endpoint not implemented yet.")


@router.get("/users/{user_id}/pending-invites")
async def get_user_pending_invites(user_id: int, client: httpx.AsyncClient = Depends(get_http_client)):
    """Return events to which the user was invited but hasn't responded."""
    raise NotImplementedError("Endpoint not implemented yet.")


@router.get("/users/{user_id}/debts-summary")
async def get_user_debts_summary(user_id: int, client: httpx.AsyncClient = Depends(get_http_client)):
    """Return overall debt and credit summary for a user."""
    raise NotImplementedError("Endpoint not implemented yet.")


@router.get("/reports/validation-issues")
async def get_reports_validation_issues(client: httpx.AsyncClient = Depends(get_http_client)):
    """Return a report of data issues: missing declarations, mismatched totals, etc."""
    raise NotImplementedError("Endpoint not implemented yet.")
