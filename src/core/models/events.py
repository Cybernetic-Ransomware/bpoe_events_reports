from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.core.models.participants import Participant


class Location(BaseModel):
    id: UUID
    name: str
    entered_at: datetime
    exited_at: datetime

class EventData(BaseModel):
    id: UUID
    opened_at: datetime
    closed_at: datetime
    name: str
    locations: list[Location]
    participants: list[Participant]
    owners: list[Participant]
    total_cost: float | None = Field(default=None)

class EventNotFound(BaseModel):
    detail: str

class EventSummary(BaseModel):
    summary: EventData

class EventSummaryList(BaseModel):
    summaries: list[EventSummary]


class EventLocationOut(BaseModel):
    id: UUID
    name: str
    entered_at: datetime | None = None
    exited_at: datetime | None = None
    latitude: float | None = None
    longitude: float | None = None

    class Config:
        from_attributes = True

class EventLocationList(BaseModel):
    locations: list[EventLocationOut]


class ParticipantSettlementStatus(BaseModel):
    participant_id: UUID
    name: str
    email: str
    accepted: bool
    accepted_at: datetime | None
    settled: bool
    settled_at: datetime | None
    total_spent: float
    currency: str = "PLN"

class EventSettlementStatus(BaseModel):
    event_id: UUID
    participants: list[ParticipantSettlementStatus]


class EventQuickInfo(BaseModel):
    id: UUID
    name: str
    opened_at: datetime
    closed_at: datetime | None
    participant_count: int
    location_count: int
    transaction_count: int

class UserOwnedEventsResponse(BaseModel):
    events: list[EventQuickInfo]


