from app.models.payments import PaymentsOrm
from app.repositories.base import BaseRepository
from app.schemas.payments import PaymentResponse


class PaymentsRepository(BaseRepository):
    model = PaymentsOrm
    schema = PaymentResponse
