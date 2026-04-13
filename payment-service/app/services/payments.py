import socket
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import (
    ObjectNotFoundException,
    PaymentNotFoundException,
    ProviderEmptyResponseExceptions,
    DatabaseNotUnavailableException,
)
from app.core.logger import logger
from app.integrations.payment_provider_client import PaymentProviderClient
from app.models.payments import StatusEnum
from app.schemas.outbox import OutboxCreate
from app.schemas.payments import PaymentCreateRequest, PaymentResponse
from app.services.base import BaseService


class PaymentsService(BaseService):
    async def get_payment(self, payment_id: UUID) -> PaymentResponse:
        try:
            payment = await self.db.payments.get_one(id=payment_id)
            return payment
        except ObjectNotFoundException as ex:
            raise PaymentNotFoundException from ex
        except (SQLAlchemyError, socket.error) as ex:
            logger.error("Database connection error during fetch", error=ex)
            raise DatabaseNotUnavailableException from ex

    async def create_payment(
        self,
        payment_data: PaymentCreateRequest,
        provider: PaymentProviderClient
    ) -> tuple[PaymentResponse, bool]:
        try:
            existing_payment = await self.db.payments.get_one_or_none(idempotency_key=payment_data.idempotency_key)
            if existing_payment:
                return existing_payment, False

            new_payment = await self.db.payments.add(payment_data)
            await self.db.commit()
        except (SQLAlchemyError, socket.error) as ex:
            logger.error("Database connection error during fetch", error=ex)
            raise DatabaseNotUnavailableException from ex

        try:
            res = await provider.process_payment(new_payment.model_dump(mode="json"))
            if not res:
                raise ProviderEmptyResponseExceptions

            new_payment.status = StatusEnum.COMPLETED
        except Exception:
            new_payment.status = StatusEnum.FAILED

        outbox_data = OutboxCreate(event_type="PaymentCreate", payload=new_payment.model_dump(mode="json"))

        try:
            await self.db.payments.update(new_payment, id=new_payment.id)
            await self.db.outbox.add(outbox_data)
            await self.db.commit()
        except Exception as ex:
            logger.error("Database connection error during fetch", error=ex)
            raise DatabaseNotUnavailableException from ex

        return new_payment, True
