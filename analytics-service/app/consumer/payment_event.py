import asyncio

from aiokafka import AIOKafkaConsumer
from pydantic import ValidationError

from app.core.config import settings
from app.core.database import async_session_maker
from app.core.logger import logger
from app.repositories.processed_events import ProcessedEventsRepository
from app.repositories.transactions import TransactionsRepository
from app.schemas.kafka import KafkaPaymentEvent
from app.schemas.processed_events import ProcessedEventCreate
from app.schemas.transactions import TransactionCreate


class PaymentEventConsumer:
    def __init__(self):
        self.consumer = AIOKafkaConsumer(
            "payments_events",
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_URL,
            group_id=settings.KAFKA_CONSUMER_GROUP,
            enable_auto_commit=False,
        )

    async def consume(self):
        logger.info("PaymentEventConsumer start")
        await self.consumer.start()
        try:
            while True:
                data = await self.consumer.getmany(timeout_ms=1000)
                if not data:
                    continue

                async with async_session_maker() as session:
                    for _, messages in data.items():
                        for message in messages:
                            try:
                                event_data = KafkaPaymentEvent.model_validate_json(message.value)
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

                                processed_event_data = ProcessedEventCreate(
                                    event_id=event_data.event_id
                                )

                                await TransactionsRepository(session).add(transaction_data)
                                await ProcessedEventsRepository(session).add(processed_event_data)

                            except ValidationError as ex:
                                logger.error("Schema ValidationError", data=message.value, error=ex)
                                continue

                            except Exception as ex:
                                logger.error("Unexpected error", data=message.value, error=ex)
                                continue

                    await session.commit()
                    await self.consumer.commit()

        except asyncio.CancelledError:
            logger.info("PaymentEventConsumer shutdown")
            raise

        finally:
            await self.consumer.stop()
