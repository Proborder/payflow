import asyncio
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from aiokafka import AIOKafkaProducer
from fastapi import FastAPI

sys.path.append(str(Path(__file__).parent.parent))

from app.api.health import router as health_router
from app.api.middleware import LoggingMiddleware
from app.api.payments import router as payment_router
from app.core.config import settings
from app.core.logger import logger, setup_logging
from app.integrations.kafka.outbox_relay import outbox_relay_worker

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting_payment_service")
    # TODO: Надо вынести продюсер
    producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_URL, enable_idempotence=True)
    outbox_task = asyncio.create_task(outbox_relay_worker(producer))

    yield

    outbox_task.cancel()
    logger.info("stopping_payment_service")


app = FastAPI(
    title="Payment Service API",
    lifespan=lifespan,
)

app.add_middleware(LoggingMiddleware)

app.include_router(health_router, prefix="/api/v1")
app.include_router(payment_router, prefix="/api/v1")
