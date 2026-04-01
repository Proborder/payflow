import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class OutboxCreate(BaseModel):
    event_type: str
    payload: dict[str, Any]


class Outbox(OutboxCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    published: bool
