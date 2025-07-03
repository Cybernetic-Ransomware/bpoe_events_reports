from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class Location(BaseModel):
    id: UUID
    name: str
    entered_at: datetime
    exited_at: datetime

class Participant(BaseModel):
    id: UUID
    name: str
    email: EmailStr

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


class EventTransactionItem(BaseModel):
    id: int
    event_id: int
    amount: Decimal = Field(..., description="Total transaction amount")
    currency: str = Field(..., min_length=3, max_length=3)
    description: str | None = None
    timestamp: datetime
    participant: str = Field(..., description="Display name of the participant")

class EventTransactionList(BaseModel):
    items: list[EventTransactionItem]

class DateRange(BaseModel):
    start: date
    end: date

class EventFinancialBreakdown(BaseModel):
    event_id: int
    event_name: str
    total_paid: Decimal
    total_received: Decimal

class UserFinancialSummary(BaseModel):
    total_paid: Decimal
    total_received: Decimal
    currency: str = "PLN"
    event_count: int
    time_range: DateRange
    details: list[EventFinancialBreakdown] = []

class InvitedParticipant(BaseModel):
    id: UUID
    name: str
    email: EmailStr

class AcceptedParticipant(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    accepted_at: datetime
    settled: bool
    settled_at: datetime | None

class InvitedParticipantList(BaseModel):
    participants: list[InvitedParticipant]

class AcceptedParticipantList(BaseModel):
    participants: list[AcceptedParticipant]
