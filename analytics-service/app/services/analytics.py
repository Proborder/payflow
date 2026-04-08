import json
import uuid
from datetime import date

from redis.exceptions import RedisError

from app.core.config import settings
from app.core.exceptions import ObjectNotFoundException, TransactionNotFoundException
from app.core.logger import logger
from app.core.redis_conn import redis_manager
from app.services.base import BaseService


class AnalyticsService(BaseService):
    async def summary(self, date_from: date, date_to: date, currency: str):
        key = f"summary-{date_from}-{date_to}-{currency}"
        summary_from_cache = None

        try:
            summary_from_cache = await redis_manager.get(key)
        except (RedisError, ConnectionError) as ex:
            logger.warning("Redis is unavailable", error=ex)

        if not summary_from_cache:
            logger.info(f"Summary data for key: {key}. Fetching from DB")
            data = await self.db.transactions.get_analytics_summary(
                date_from=date_from,
                date_to=date_to,
                currency=currency
            )
            try:
                await redis_manager.set(key, data.model_dump_json(), settings.REDIS_SUMMARY_EXPIRE)
            except (RedisError, ConnectionError) as ex:
                logger.warning("Redis is unavailable", error=ex)

            logger.info(f"Summary data returned from DB for key: {key}")
            return data
        else:
            logger.info(f"Summary data returned from cache for key: {key}")
            return json.loads(summary_from_cache)

    async def get_transactions(
        self,
        pagination,
        status: str | None,
        currency: str | None,
        date_from: date,
        date_to: date
    ):
        per_page = pagination.per_page or 15
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
