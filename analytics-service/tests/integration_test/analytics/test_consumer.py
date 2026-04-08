import asyncio
import json
import uuid
from itertools import chain, repeat

from aiokafka import TopicPartition, ConsumerRecord

from app.consumer.payment_event import PaymentEventConsumer
from app.schemas.processed_events import ProcessedEventCreate
from app.services.db_manager import DBManager


def create_kafka_record(payload: dict, topic: str = "payments_events") -> dict:
    raw_value = json.dumps(payload).encode("utf-8")
    tp = TopicPartition(topic, 0)
    record = ConsumerRecord(
        topic=topic, partition=0, offset=1, timestamp=0,
        timestamp_type=0, key=None, value=raw_value, checksum=None,
        serialized_key_size=-1, serialized_value_size=-1, headers=[]
    )
    return {tp: [record]}


async def test_successful_event_processing(db: DBManager, mock_kafka_consumer):
    payload = {
        "event_id": "a9a2f56e-f1d1-4790-bbc3-bb928891f53f",
        "event_type": "payment.completed",
        "payment_id": "017c2e5d-2b1c-4fa4-856e-ef674c86d15a",
        "amount": 500,
        "currency": "RUB",
        "status": "COMPLETED",
        "timestamp": "2026-04-01T08:32:09.668494",
    }

    data = create_kafka_record(payload)
    mock_kafka_consumer.getmany.side_effect = chain([data], repeat({}))

    consumer = PaymentEventConsumer()
    stop_event = asyncio.Event()

    task = asyncio.create_task(consumer.consume(stop_event))
    await asyncio.sleep(0.1)
    stop_event.set()
    await asyncio.wait_for(task, timeout=2.0)

    transaction = await db.transactions.get_one_or_none(payment_id=payload["payment_id"])

    assert transaction is not None
    assert transaction.amount == 500
    assert transaction.currency == "RUB"

    processed_event = await db.processed_events.get_one_or_none(event_id=payload["event_id"])

    assert processed_event is not None


async def test_idempotency_no_duplicates_in_db(db: DBManager, mock_kafka_consumer):
    event_id = uuid.uuid4()
    processed_event_data = ProcessedEventCreate(event_id=event_id)
    await db.processed_events.add(processed_event_data)
    await db.commit()

    payload = {
        "event_id": str(event_id),
        "event_type": "payment.completed",
        "payment_id": "017c2e5d-2b1c-4fa4-856e-ef674c86d15a",
        "amount": 100,
        "currency": "USD",
        "status": "COMPLETED",
        "timestamp": "2026-04-01T08:32:09.668494",
    }

    data = create_kafka_record(payload)
    mock_kafka_consumer.getmany.side_effect = chain([data], repeat({}))

    consumer = PaymentEventConsumer()
    stop_event = asyncio.Event()

    task = asyncio.create_task(consumer.consume(stop_event))
    await asyncio.sleep(0.1)
    stop_event.set()
    await asyncio.wait_for(task, timeout=2.0)

    processed_event = await db.processed_events.get_all(event_id=payload["event_id"])

    assert processed_event is not None
    assert len(processed_event) == 1
