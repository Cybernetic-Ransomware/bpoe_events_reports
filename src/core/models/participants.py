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


class UserPendingInvite(BaseModel):
    event_id: UUID
    name: str
    opened_at: datetime
    invited_by: str
    invitation_sent_at: datetime

class UserPendingInvitesResponse(BaseModel):
    events: list[UserPendingInvite]
