from uuid import UUID

from app.core.exceptions import (
    CircuitBreakerBlockedRequestExceptions,
    ObjectNotFoundException,
    PaymentNotFoundException,
    ProviderConnectionExceptions,
    ProviderEmptyResponseExceptions,
)
from app.integrations.payment_provider_client import PaymentProviderClient
from app.models.payments import StatusEnum
from app.schemas.outbox import OutboxCreate
from app.schemas.payments import PaymentCreateRequest, PaymentResponse
from app.services.base import BaseService
from app.services.db_manager import DBManager


class PaymentsService(BaseService):
    def __init__(self, db: DBManager):
        super().__init__(db)

    async def get_payment(self, payment_id: UUID) -> PaymentResponse:
        try:
            payment = await self.db.payments.get_one(id=payment_id)
            return payment
        except ObjectNotFoundException as ex:
            raise PaymentNotFoundException from ex

    async def create_payment(
        self,
        payment_data: PaymentCreateRequest,
        provider: PaymentProviderClient
    ) -> tuple[PaymentResponse, bool]:
        existing_payment = await self.db.payments.get_one_or_none(idempotency_key=payment_data.idempotency_key)
        if existing_payment:
            return existing_payment, False

        new_payment = await self.db.payments.add(payment_data)
        await self.db.commit()

        try:
            res = await provider.process_payment(new_payment.model_dump(mode="json"))
            if not res:
                raise ProviderEmptyResponseExceptions

            new_payment.status = StatusEnum.COMPLETED
        except (ProviderEmptyResponseExceptions, ProviderConnectionExceptions, CircuitBreakerBlockedRequestExceptions):
            new_payment.status = StatusEnum.FAILED
        finally:
            await self.db.payments.update(new_payment, id=new_payment.id)
            outbox_data = OutboxCreate(event_type="PaymentCreate", payload=new_payment.model_dump(mode="json"))
            await self.db.outbox.add(outbox_data)
            await self.db.commit()

        return new_payment, True
