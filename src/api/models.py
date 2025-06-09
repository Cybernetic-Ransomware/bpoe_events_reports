from pydantic import BaseModel


class EventData(BaseModel):
    id: int
    name: str
    total_cost: float


class EventSummary(BaseModel):
    summary: EventData
