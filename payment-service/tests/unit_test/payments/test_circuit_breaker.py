import time

import pytest

from app.core.exceptions import CircuitBreakerBlockedRequestExceptions
from app.integrations.payment_provider_client import CircuitBreaker, CircuitBreakerState


async def mock_fail_func(*args, **kwargs):
    raise Exception()


async def mock_success_func(*args, **kwargs):
    return True


class TestCircuitBreaker:
    def test_init(self) -> None:
        circuit_breaker: CircuitBreaker = CircuitBreaker(max_failure=3, recovery_delay=60)
        assert isinstance(circuit_breaker, CircuitBreaker)
        assert circuit_breaker.max_failure == 3
        assert circuit_breaker.recovery_delay == 60

    # Переход CLOSED → OPEN при превышении порога ошибок
    # В состоянии OPEN запросы отклоняются без вызова
    async def test_switching_from_closed_to_open(self):
        circuit_breaker: CircuitBreaker = CircuitBreaker(max_failure=3, recovery_delay=60)

        for _ in range(3):
            with pytest.raises(Exception):
                await circuit_breaker.call(mock_fail_func, 1, 2, a=3, b=4)

        with pytest.raises(CircuitBreakerBlockedRequestExceptions):
            await circuit_breaker.call(mock_fail_func, 1, 2, a=3, b=4)

        assert circuit_breaker.state == CircuitBreakerState.OPEN
        assert circuit_breaker.failure_count == 3

    # Переход OPEN → HALF_OPEN после таймаута
    # Успешный запрос в HALF_OPEN → CLOSED
    async def test_switching_from_open_to_half_open(self):
        circuit_breaker: CircuitBreaker = CircuitBreaker(max_failure=1, recovery_delay=5)

        with pytest.raises(Exception):
            await circuit_breaker.call(mock_fail_func, 1, 2, a=3, b=4)


        circuit_breaker.last_failure_time = time.monotonic() - 6
        await circuit_breaker.call(mock_success_func, 1, 2, a=3, b=4)
        assert circuit_breaker.state == CircuitBreakerState.CLOSED
