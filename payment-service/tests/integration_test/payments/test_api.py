import pytest
from httpx import AsyncClient


# Создание платежа (happy path) – 201, корректный ответ
async def test_create_payment_success(ac: AsyncClient, setup_database):
    response = await ac.post("/api/v1/payments", json={
        "amount": 100,
        "currency": "RUB",
        "description": "string",
        "idempotency_key": "4fa85f64-5717-4562-b3fc-4c963f66afa6",
    })

    assert response.status_code == 201


# Получение платежа по ID
async def test_get_payment_by_id(ac: AsyncClient, setup_database):
    response = await ac.post("/api/v1/payments", json={
        "amount": 50,
        "currency": "EUR",
        "description": "string",
        "idempotency_key": "550e8400-e29b-41d4-a716-446655440000",
    })

    payment_id = response.json()["id"]
    response = await ac.get(f"/api/v1/payments/{payment_id}")

    assert response.status_code == 200
    assert response.json()["id"] == payment_id


# Получение несуществующего платежа – 404
async def test_get_payment_not_found(ac: AsyncClient, setup_database):
    fake_id = "db12b761-8322-49c9-bea2-26f1baff2645"
    response = await ac.get(f"/api/v1/payments/{fake_id}")

    assert response.status_code == 404


# Идемпотентность: повторный запрос с тем же idempotency_key не создаёт дубликат
@pytest.mark.parametrize(
    "status_code",
    [
        201,
        200
    ]
)
async def test_create_payment_idempotence(
    status_code,
    ac: AsyncClient,
    setup_database
):
    response = await ac.post("/api/v1/payments", json={
        "amount": 100,
        "currency": "RUB",
        "description": "string",
        "idempotency_key": "3fa85f64-5717-4562-b3fc-5c961f66afa2",
    })

    assert response.status_code == status_code


# Валидация: отрицательная сумма, невалидная валюта – 422
@pytest.mark.parametrize(
    "amount, currency, status_code",
    [
        (-5, "RUB", 422),
        (100, "INVALID", 422),
        (0, "RUB", 422)
    ],
)
async def test_create_payment_validation_errors(
    amount,
    currency,
    status_code,
    ac: AsyncClient,
    setup_database
):
    response = await ac.post("/api/v1/payments", json={
        "amount": amount,
        "currency": currency,
        "description": "string",
        "idempotency_key": "3fa85f62-5717-4562-b1fc-5c961f46afa1",
    })

    assert response.status_code == status_code
