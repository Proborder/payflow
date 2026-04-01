import asyncio
from datetime import datetime

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from app.core.database import async_session_maker
from app.core.logger import logger
from app.repositories.outbox import OutboxRepository
from app.schemas.kafka import KafkaPaymentEvent


async def outbox_relay_worker(producer: AIOKafkaProducer):
    logger.info("Outbox Relay worker start")
    await producer.start()
    try:
        while True:
            async with async_session_maker() as session:
                unhandled_events = await OutboxRepository(session).get_all(published=False)
                for event in unhandled_events:
                    event_type = (
                        "payment.completed"
                        if event.payload["status"] == "COMPLETED"
                        else "payment.failed"
                    )
                    data = KafkaPaymentEvent(
                        event_id=event.id,
                        event_type=event_type,
                        payment_id=event.payload["id"],
                        amount=event.payload["amount"],
                        currency=event.payload["currency"],
                        status=event.payload["status"],
                        timestamp=datetime.now(),
                    )

                    try:
                        await producer.send_and_wait(
                            topic="payments_events",
                            value=data.model_dump_json().encode("utf-8"),
                            key=str(event.payload["id"]).encode("utf-8"),
                        )
                    except KafkaError as ex:
                        logger.error(f"Failed to send event to Kafka\nData: {data}: {ex}")
                        continue

                    event.published = True
                    await OutboxRepository(session).update(event, id=event.id)
                    await session.commit()

            await asyncio.sleep(30)
    except asyncio.CancelledError:
        logger.info("Outbox Relay worker shutdown")
    finally:
        await producer.stop()
