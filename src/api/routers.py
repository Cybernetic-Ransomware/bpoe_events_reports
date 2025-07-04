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
from src.config.conf_logger import setup_logger
from src.core import models

logger = setup_logger(__name__, "api")

router = APIRouter()


@router.get("/", include_in_schema=False)
async def healthcheck():
    logger.info("Called second healthcheck [API router]")
    return {"status": "OK"}


@router.get("/events/{event_id}/summary", response_model=models.EventSummary)
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
        data = models.EventData.model_validate(data_json)
        return models.EventSummary(summary=data)

    except PydanticValidationError as e:
        try:
            models.EventNotFound.model_validate(data_json)
            raise ValueNotFoundError(event_id=event_id) from e
        except ValidationError:
            raise ExternalServiceUnexpectedError(
                service_name="DB Handler", original_error=e
            ) from e


@router.get("/users/{user_id}/events/summary", response_model=models.EventSummaryList)
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

    summaries = [models.EventSummary.model_validate(item) for item in data_json]
    return models.EventSummaryList(summaries=summaries)


@router.get("/events/{event_id}/costs/details")
async def get_event_cost_details(event_id: UUID, client: httpx.AsyncClient = Depends(get_http_client)):
    """
    Retrieve and return a list of validated cost breakdown for a specific event.

    Data is fetched from the DB Handler service and parsed into EventTransactionItem models.
    If the response structure is invalid or unexpected, an ExternalServiceUnexpectedError is raised.

    Parameters:
    - event_id: UUID of the event to retrieve cost details for.
    - client: HTTP client used for communication with the DB Handler (injected dependency).

    Returns:
    - EventTransactionList object containing validated cost transactions.
    """
    url = f"events/{event_id}/costs/details"
    data_json = await fetch_from_service(client, url)

    transactions = [models.EventTransactionItem.model_validate(item) for item in data_json]
    return models.EventTransactionList(items=transactions)


@router.get("/users/{user_id}/events/financial-summary")
async def get_user_financial_summary(
        user_id: int,
        date_range: tuple[pendulum.DateTime, pendulum.DateTime] = Depends(get_date_range),
        client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Retrieve and return a financial summary for all events of a specific user within a given date range.

    Data is fetched from the DB Handler service and validated against the UserFinancialSummary model.
    If the structure of the response is invalid or unexpected, an ExternalServiceUnexpectedError is raised.

    Parameters:
    - user_id: ID of the user whose financial summary is to be fetched.
    - date_range: Tuple containing the start and end date as Pendulum DateTime objects.
    - client: HTTP client used for communication with the DB Handler (injected dependency).

    Returns:
    - A validated UserFinancialSummary object.
    """
    start, end = date_range
    url = f"users/{user_id}/events/financial-summary"
    params = {"start_date": start.to_date_string(), "end_date": end.to_date_string()}

    data_json = await fetch_from_service(client, url, params=params)

    return models.UserFinancialSummary.model_validate(data_json)


@router.get("/events/{event_id}/participants/invited", response_model=models.InvitedParticipantList)
async def get_invited_participants(
    event_id: UUID,
    client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Retrieve and return a list of participants invited to a specific event.

    Data is fetched from the DB Handler service and validated against the InvitedParticipant model.
    If the structure of the response is invalid or unexpected, an ExternalServiceUnexpectedError is raised.

    Parameters:
    - event_id: UUID of the event to fetch invited participants for.
    - client: HTTP client used for communication with the DB Handler (injected dependency).

    Returns:
    - An InvitedParticipantList object containing validated invited participants.
    """
    url = f"events/{event_id}/participants/invited"
    data_json = await fetch_from_service(client, url)

    participants = [models.InvitedParticipant.model_validate(item) for item in data_json]
    return models.InvitedParticipantList(participants=participants)


@router.get("/events/{event_id}/participants/accepted", response_model=models.AcceptedParticipantList)
async def get_accepted_participants(
    event_id: UUID,
    client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Retrieve and return a list of participants who accepted the invitation and their settlement declarations.

    Data is fetched from the DB Handler service and validated against the AcceptedParticipant model.
    If the structure of the response is invalid or unexpected, an ExternalServiceUnexpectedError is raised.

    Parameters:
    - event_id: UUID of the event to fetch accepted participants for.
    - client: HTTP client used for communication with the DB Handler (injected dependency).

    Returns:
    - An AcceptedParticipantList object containing validated accepted participants with settlement info.
    """
    url = f"events/{event_id}/participants/accepted"
    data_json = await fetch_from_service(client, url)

    participants = [models.AcceptedParticipant.model_validate(item) for item in data_json]
    return models.AcceptedParticipantList(participants=participants)


@router.get("/events/{event_id}/locations", response_model=models.EventLocationList)
async def get_event_locations(
    event_id: UUID,
    client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Retrieve and return locations associated with a specific event, including coordinates, entry and exit timestamps.

    Data is fetched from the DB Handler service and validated against the EventLocationOut model.
    If the structure of the response is invalid or unexpected, an ExternalServiceUnexpectedError is raised.

    Parameters:
    - event_id: UUID of the event whose location history is to be fetched.
    - client: HTTP client used for communication with the DB Handler (injected dependency).

    Returns:
    - An EventLocationList object containing a list of event locations with timestamps.
    """
    url = f"events/{event_id}/locations"
    data_json = await fetch_from_service(client, url)

    locations = [models.EventLocationOut.model_validate(item) for item in data_json]
    return models.EventLocationList(locations=locations)


@router.get("/events/{event_id}/participants/settlement-status")
async def get_participant_settlement_status(
        event_id: UUID,
        client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Retrieve the settlement status of all participants for a specific event.

    Fetches participant associations (acceptance + settlement), their declared info,
    and total amount spent by each participant within a given event.

    Parameters:
    - event_id: UUID of the event.
    - client: HTTP client used for communication with the DB Handler (injected dependency).

    Returns:
    - EventSettlementStatus model containing participant statuses and declared financial data.
    """
    url = f"events/{event_id}/participants/settlement-status"
    data_json = await fetch_from_service(client, url)

    return models.EventSettlementStatus.model_validate(data_json)


@router.get("/users/{user_id}/events/owned")
async def get_owned_events(
        user_id: int,
        date_range: tuple[pendulum.DateTime, pendulum.DateTime] = Depends(get_date_range),
        client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Retrieve events owned by a specific user within a given date range.

    Fetches event metadata for which the specified user is the owner,
    limited to events with opening dates between `start_date` and `end_date`.

    Parameters:
    - user_id: ID of the user.
    - date_range: Tuple of start and end dates to filter events by their opening date.
    - client: HTTP client used for communication with the DB Handler (injected dependency).

    Returns:
    - UserOwnedEventsResponse model containing a list of event metadata owned by the user.
    """
    start, end = date_range
    url = f"users/{user_id}/events/owned"
    params = {"start_date": start.to_date_string(), "end_date": end.to_date_string()}

    data_json = await fetch_from_service(client, url, params=params)

    return models.UserOwnedEventsResponse.model_validate({"events": data_json})


@router.get("/users/{user_id}/events/unsettled")
async def get_unsettled_events(
        user_id: int,
        date_range: tuple[pendulum.DateTime, pendulum.DateTime] = Depends(get_date_range),
        client: httpx.AsyncClient = Depends(get_http_client)
):
    """
    Retrieve events with incomplete settlements for a specific user.

    Fetches events in which the user is a confirmed participant (accepted)
    but has not completed their settlement process. Filters by event opening date.

    Parameters:
    - user_id: ID of the user.
    - date_range: Tuple of start and end dates to filter events by their opening date.
    - client: Injected async HTTP client for backend service communication.

    Returns:
    - UserUnsettledEventsResponse model containing event IDs, names, dates and participant-level settlement data.
    """
    start, end = date_range
    url = f"users/{user_id}/events/unsettled"
    params = {"start_date": start.to_date_string(), "end_date": end.to_date_string()}

    data_json = await fetch_from_service(client, url, params=params)

    return models.UserUnsettledEventsResponse.model_validate({"events": data_json})


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
