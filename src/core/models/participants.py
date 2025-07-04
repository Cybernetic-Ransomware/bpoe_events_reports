from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class Participant(BaseModel):
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
    participants: list[Participant]

class AcceptedParticipantList(BaseModel):
    participants: list[AcceptedParticipant]
