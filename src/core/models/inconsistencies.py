from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class ValidationIssue(BaseModel):
    timestamp: datetime
    level: str
    message: str

class DeclarationIssue(BaseModel):
    event_id: UUID
    participant_id: int
    reason: str

class TotalMismatch(BaseModel):
    event_id: UUID
    expected_total: Decimal
    declared_total: Decimal

class OrphanedTransaction(BaseModel):
    transaction_id: UUID
    reason: str

class ValidationIssuesReport(BaseModel):
    missing_declarations: list[DeclarationIssue]
    mismatched_totals: list[TotalMismatch]
    orphaned_transactions: list[OrphanedTransaction]
