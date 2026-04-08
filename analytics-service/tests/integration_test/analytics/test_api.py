import pytest
from httpx import AsyncClient


# Получение summary – корректные агрегации
@pytest.mark.parametrize(
    "date_from, date_to, currency, total_count, completed_count, failed_count",
    [
        ("2026-04-04", "2026-04-08", "RUB", 12, 12, 0),
        ("2026-04-05", "2026-04-09", "USD", 1, 0, 1)
    ]
)
async def test_get_summary_aggregations(
    date_from,
    date_to,
    currency,
    total_count,
    completed_count,
    failed_count,
    ac: AsyncClient,
    setup_database
):
    response = await ac.get("/api/v1/analytics/summary", params={
        "date_from": date_from,
        "date_to": date_to,
        "currency": currency
    })

    assert response.status_code == 200
    assert response.json()["total_count"] == total_count
    assert response.json()["completed_count"] == completed_count
    assert response.json()["failed_count"] == failed_count


# Фильтрация по статусу, валюте, периоду
@pytest.mark.parametrize(
    "status, currency, date_from, date_to, count",
    [
        ("COMPLETED", "RUB", "2026-04-04", "2026-04-06", 0),
        ("COMPLETED", "RUB", "2026-04-04", "2026-04-07", 12),
        ("FAILED", "USD", "2026-04-07", "2026-04-09", 1),
    ]
)
async def test_transaction_filtering(
    status,
    currency,
    date_from,
    date_to,
    count,
    ac: AsyncClient,
    setup_database
):
    response = await ac.get("/api/v1/analytics/transactions", params={
        "status": status,
        "currency": currency,
        "date_from": date_from,
        "date_to": date_to
    })

    assert response.status_code == 200
    assert len(response.json()) == count


# Список транзакций с пагинацией
@pytest.mark.parametrize(
    "page, per_page, count",
    [
        (1, 1, 1),
        (3, 4, 4),
        (1, 5, 5)
    ]
)
async def test_get_transactions_with_pagination(
    page,
    per_page,
    count,
    ac: AsyncClient,
    setup_database
):
    response = await ac.get("/api/v1/analytics/transactions", params={
        "page": page,
        "per_page": per_page,
    })

    assert response.status_code == 200
    assert len(response.json()) == count


# Получение несуществующей транзакции – 404
async def test_get_transaction_not_found(ac: AsyncClient, setup_database):
    fake_id = "db12b761-8322-49c9-bea2-26f1baff2645"
    response = await ac.get(f"/api/v1/analytics/transactions/{fake_id}")

    assert response.status_code == 404
