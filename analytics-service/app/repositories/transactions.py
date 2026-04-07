from datetime import date

from sqlalchemy import select, func

from app.models.transactions import TransactionsOrm
from app.repositories.base import BaseRepository
from app.schemas.transactions import Transaction, AnalyticsSummary


class TransactionsRepository(BaseRepository):
    model = TransactionsOrm
    schema = Transaction

    async def get_filtered_by_time(
        self,
        status: str,
        currency: str,
        date_from: date,
        date_to: date,
        limit: int,
        offset: int,
    ) -> list[Transaction]:
        query = select(TransactionsOrm)

        if status:
            query = query.filter(TransactionsOrm.status == status)
        if currency:
            query = query.filter(TransactionsOrm.currency == currency)
        if date_from:
            query = query.filter(TransactionsOrm.processed_at >= date_from)
        if date_to:
            query = query.filter(TransactionsOrm.processed_at <= date_to)

        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)

        return [Transaction.model_validate(model, from_attributes=True) for model in result.scalars().all()]

    async def get_analytics_summary(self, date_from: date, date_to: date, currency: str) -> AnalyticsSummary:
        query = select(
            func.count(TransactionsOrm.id).label("total_count"),
            func.coalesce(func.sum(TransactionsOrm.amount), 0).label("total_amount"),
            func.count(TransactionsOrm.id).filter(TransactionsOrm.status == "COMPLETED").label("completed_count"),
            func.count(TransactionsOrm.id).filter(TransactionsOrm.status == "FAILED").label("failed_count"),
            func.coalesce(func.avg(TransactionsOrm.amount), 0).label("average_check"),
        )

        if date_from:
            query = query.filter(TransactionsOrm.processed_at >= date_from)
        if date_to:
            query = query.filter(TransactionsOrm.processed_at <= date_to)
        if currency:
            query = query.filter(TransactionsOrm.currency == currency)

        result = await self.session.execute(query)
        model = result.one()

        return AnalyticsSummary.model_validate(model, from_attributes=True)
