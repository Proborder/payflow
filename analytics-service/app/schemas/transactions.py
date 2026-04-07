import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class TransactionCreate(BaseModel):
    payment_id: uuid.UUID
    amount: Decimal
    currency: str
    status: str
    event_type: str
    processed_at: datetime


class Transaction(TransactionCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID


class AnalyticsSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_count: int
    total_amount: Decimal
    completed_count: int
    failed_count: int
    average_check: Decimal
