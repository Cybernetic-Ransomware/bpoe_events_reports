from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


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
