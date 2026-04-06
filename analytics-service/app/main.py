import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.middleware import LoggingMiddleware
from app.consumer.payment_event import PaymentEventConsumer
from app.core.logger import logger
from app.core.redis_conn import redis_manager
from app.api.health import router as health_router
from app.api.analytics import router as analytics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting_analytics_service")

    await redis_manager.connect()
    consumer = PaymentEventConsumer()
    consumer_task = asyncio.create_task(consumer.consume())

    yield

    await redis_manager.close()
    consumer_task.cancel()

    try:
        await asyncio.wait_for(asyncio.shield(consumer_task), timeout=10.0)
    except asyncio.CancelledError:
        logger.info("Consumer task cancelled successfully")
    except asyncio.TimeoutError:
        logger.error("Consumer task timed out during shutdown")
    except Exception as ex:
        logger.error(f"Error during consumer shutdown: {ex}")

    logger.info("stopping_payment_service")


app = FastAPI(
    title="Analytics Service API",
    lifespan=lifespan
)

app.add_middleware(LoggingMiddleware)

app.include_router(health_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
