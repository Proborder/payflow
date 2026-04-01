import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.payments import StatusEnum


class PaymentCreateRequest(BaseModel):
    amount: Decimal = Field(max_digits=10, decimal_places=2)
    currency: str
    description: str = Field(max_length=100)
    idempotency_key: uuid.UUID

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v) -> Decimal:
        if v <= 0:
            raise ValueError("Сумма должна быть положительная")
        return v

    @field_validator("currency")
    @classmethod
    def correct_currency(cls, v) -> str:
        if len(v) != 3 or not isinstance(v, str):
            raise ValueError("Неверная валюта")
        return v


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    amount: Decimal
    currency: str
    status: StatusEnum
    description: str
    created_at: datetime
    updated_at: datetime
