import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class KafkaPaymentEvent(BaseModel):
    event_id: uuid.UUID
    event_type: str
    payment_id: uuid.UUID
    amount: Decimal
    currency: str
    status: str
    timestamp: datetime
