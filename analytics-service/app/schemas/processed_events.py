import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProcessedEventCreate(BaseModel):
    event_id: uuid.UUID


class ProcessedEvent(ProcessedEventCreate):
    model_config = ConfigDict(from_attributes=True)

    processed_at: datetime
