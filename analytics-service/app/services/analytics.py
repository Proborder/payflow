import uuid
from datetime import date

from app.core.exceptions import ObjectNotFoundException, TransactionNotFoundException
from app.services.base import BaseService


class AnalyticsService(BaseService):
    async def summary(self, date_from: date, date_to: date, currency: str):
        return await self.db.transactions.get_analytics_summary(
            date_from=date_from,
            date_to=date_to,
            currency=currency
        )

    async def get_transactions(
        self,
        pagination,
        status: str | None,
        currency: str | None,
        date_from: date,
        date_to: date
    ):
        per_page = pagination.per_page or 5
        return await self.db.transactions.get_filtered_by_time(
            status=status,
            currency=currency,
            date_from=date_from,
            date_to=date_to,
            limit=per_page,
            offset=per_page * (pagination.page - 1)
        )

    async def get_transaction(self, payment_id: uuid.UUID):
        try:
            transaction = await self.db.transactions.get_one(payment_id=payment_id)
            return transaction
        except ObjectNotFoundException as ex:
            raise TransactionNotFoundException from ex
