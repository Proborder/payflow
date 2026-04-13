import asyncio

from aiokafka import AIOKafkaConsumer, ConsumerRecord
from aiokafka.errors import KafkaError, CommitFailedError
from pydantic import ValidationError
from redis import RedisError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import async_session_maker
from app.core.logger import logger
from app.core.redis_conn import redis_manager
from app.repositories.processed_events import ProcessedEventsRepository
from app.repositories.transactions import TransactionsRepository
from app.schemas.kafka import KafkaPaymentEvent
from app.schemas.processed_events import ProcessedEventCreate
from app.schemas.transactions import TransactionCreate


class PaymentEventConsumer:
    def __init__(self):
        self.consumer: AIOKafkaConsumer = AIOKafkaConsumer(
            "payments_events",
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_URL,
            group_id=settings.KAFKA_CONSUMER_GROUP,
            enable_auto_commit=False,
        )

    async def consume(self, stop_event: asyncio.Event):
        logger.info("PaymentEventConsumer start")
        await self.consumer.start()
        try:
            while not stop_event.is_set():
                await asyncio.sleep(0)
                try:
                    data = await self.consumer.getmany(
                        timeout_ms=settings.KAFKA_CONSUMER_TIMEOUT,
                        max_records=settings.KAFKA_CONSUMER_MAX_RECORDS,
                    )
                except KafkaError as ex:
                    logger.error("Kafka connection lost or error occurred", error=ex)
                    await asyncio.sleep(5)
                    continue

                if not data:
                    continue

                async with async_session_maker() as session:
                    try:
                        for _, messages in data.items():
                            await self.event_handling(session, messages)

                        await session.commit()

                        try:
                            await self.consumer.commit()
                        except CommitFailedError as ex:
                            logger.warning("Kafka rebalance occurred. Batch processed but offset not committed", error=ex)

                        try:
                            count_of_deleted_keys = await redis_manager.delete_by_mask("summary-*")
                            if count_of_deleted_keys:
                                logger.info(f"Cleared {count_of_deleted_keys} summary keys from cache")
                        except (RedisError, ConnectionError):
                            logger.warning("Redis unavailable, cache not cleared")

                    except (SQLAlchemyError, Exception) as ex:
                        logger.error("Database connection lost or error occurred", error=ex)
                        await session.rollback()

                        for tp, messages in data.items():
                            first_offset = messages[0].offset
                            logger.info(f"Seeking back to offset {first_offset} for partition {tp.partition}")
                            self.consumer.seek(tp, first_offset)

                        await asyncio.sleep(5)
                        continue

                    # except Exception as ex:
                    #     logger.error("Unexpected error", error=ex)
                    #     await session.rollback()

        except asyncio.CancelledError:
            logger.info("PaymentEventConsumer shutdown")

        finally:
            await self.consumer.stop()
            logger.info("PaymentEventConsumer shutdown")

    async def event_handling(self, session: AsyncSession, messages: list[ConsumerRecord]) -> None:
        for message in messages:
            try:
                event_data: KafkaPaymentEvent = KafkaPaymentEvent.model_validate_json(message.value)
                logger.info(f"New kafka event: {event_data.event_id} Payment: {event_data.payment_id}")

                event_exists = await (
                    ProcessedEventsRepository(session)
                    .get_one_or_none(event_id=event_data.event_id)
                )

                if event_exists:
                    logger.info(f"The event has already been processed: {event_data.event_id}")
                    continue

                transaction_data = TransactionCreate(
                    payment_id=event_data.payment_id,
                    amount=event_data.amount,
                    currency=event_data.currency,
                    status=event_data.status,
                    event_type=event_data.event_type,
                    processed_at=event_data.timestamp,
                )

                processed_event_data = ProcessedEventCreate(event_id=event_data.event_id)

                await TransactionsRepository(session).add(transaction_data)
                await ProcessedEventsRepository(session).add(processed_event_data)

            except ValidationError as ex:
                logger.error("Schema ValidationError", data=message.value, error=ex)
                continue

            except Exception as ex:
                logger.error("Unexpected error", data=message.value, error=ex)
                raise
