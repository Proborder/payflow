from app.models.outbox import OutboxOrm
from app.repositories.base import BaseRepository
from app.schemas.outbox import Outbox


class OutboxRepository(BaseRepository):
    model = OutboxOrm
    schema = Outbox
