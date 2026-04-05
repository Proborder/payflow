import uuid
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import mapped_column, Mapped

from app.core.database import Base


class ProcessedEventsOrm(Base):
    __tablename__ = 'processed_events'

    event_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    processed_at: Mapped[datetime] = mapped_column(default=func.now())
