import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.analytics import router as analytics_router
from app.api.health import router as health_router
from app.api.middleware import LoggingMiddleware
from app.consumer.payment_event import PaymentEventConsumer
from app.core.logger import logger
from app.core.redis_conn import redis_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting_analytics_service")

    stop_event = asyncio.Event()

    await redis_manager.connect()
    consumer = PaymentEventConsumer()
    consumer_task = asyncio.create_task(consumer.consume(stop_event))

    yield

    logger.info("shutting_down_analytics_service")

    stop_event.set()

    try:
        await asyncio.wait_for(consumer_task, timeout=10.0)
        logger.info("Consumer task finished cleanly")
    except TimeoutError:
        logger.error("Consumer task timed out during shutdown")
        consumer_task.cancel()
    except Exception as ex:
        logger.error("Error during consumer shutdown", error=ex)
    finally:
        await redis_manager.close()
        logger.info("stopping_analytics_service")


app = FastAPI(
    title="Analytics Service API",
    lifespan=lifespan
)

app.add_middleware(LoggingMiddleware)

app.include_router(health_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
