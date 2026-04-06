from app.models.processed_events import ProcessedEventsOrm
from app.repositories.base import BaseRepository
from app.schemas.processed_events import ProcessedEvent


class ProcessedEventsRepository(BaseRepository):
    model = ProcessedEventsOrm
    schema = ProcessedEvent
