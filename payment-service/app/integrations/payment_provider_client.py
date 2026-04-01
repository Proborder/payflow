import asyncio
import enum
import random
import time
from collections.abc import Callable
from functools import wraps

import httpx
from httpx import ConnectError, ConnectTimeout, HTTPStatusError, RequestError, Response
from starlette.responses import JSONResponse

from app.core.exceptions import CircuitBreakerBlockedRequestExceptions, ProviderConnectionExceptions
from app.core.logger import logger
from app.schemas.payments import PaymentResponse


def retry(func: Callable) -> Callable:
    attempts: int = 3
    base_delay: float = 1.0

    @wraps(func)
    async def wrapper(*args, **kwargs) -> Response | None:
        for attempt in range(attempts):
            try:
                return await func(*args, **kwargs)
            except HTTPStatusError as ex:
                if ex.response.is_client_error:
                    logger.error(f"{func.__name__} Request error. Exception: {ex}")
                    raise
                elif ex.response.is_server_error:
                    delay = (base_delay * 2 ** attempt) + random.uniform(0, 1) # noqa: S311
                    logger.error(f"{func.__name__} Request error. Retry in {delay} 5 seconds")
                    await asyncio.sleep(delay)
                elif attempt >= 2:
                    logger.exception(f"{func.__name__} All retry attempts failed.")
                    raise
            except Exception as ex:
                raise ex
        raise
    return wrapper


class CircuitBreakerState(enum.StrEnum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    def __init__(self, max_failure: int, recovery_delay: int) -> None:
        self.max_failure: int = max_failure
        self.recovery_delay: int = recovery_delay
        self.state: CircuitBreakerState = CircuitBreakerState.CLOSED
        self.failure_count: int = 0
        self.last_failure_time: float | None = None

    async def call(self, func, *args, **kwargs):
        if self.state == CircuitBreakerState.OPEN:
            if time.monotonic() - self.last_failure_time >= self.recovery_delay:
                logger.info("CircuitBreakerState switch status on HALF_OPEN")
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise CircuitBreakerBlockedRequestExceptions

        try:
            result = await func(*args, **kwargs)
            self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
            return result
        except Exception as ex:
            self.failure_count += 1
            self.last_failure_time = time.monotonic()
            if self.failure_count >= self.max_failure:
                logger.info("CircuitBreakerState switch status on OPEN")
                self.state = CircuitBreakerState.OPEN
            # logging.exception(f"{func.__name__} ...")
            raise ex


class PaymentProviderClient:
    def __init__(self, base_url: str):
        self.base_url: str = base_url
        self.circuit_breaker: CircuitBreaker = CircuitBreaker(max_failure=5, recovery_delay=60)

    @retry
    async def provider_request(self, payload) -> JSONResponse:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/process-payment", json=payload)
            response.raise_for_status()
            return response.json()

    async def process_payment(self, payload: PaymentResponse) -> Response:
        try:
            return await self.circuit_breaker.call(self.provider_request, payload)
        except (ConnectError, ConnectTimeout, RequestError) as ex:
            logger.error(f"Error connect to payment provider: {ex}")
            raise ProviderConnectionExceptions from ex
        except CircuitBreakerBlockedRequestExceptions:
            logger.error("CircuitBreaker blocked request")
            raise
