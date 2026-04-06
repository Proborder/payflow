import uuid
from datetime import date

from fastapi import APIRouter, Query

from app.api.dependencies import DBDep, PaginationDep
from app.core.exceptions import (
    TransactionNotFoundException,
    TransactionNotFoundHTTPException,
)
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary")
async def summary(
    db: DBDep,
    date_from: date | None = Query(None, description="Начало периода"),
    date_to: date | None = Query(None, description="Конец периода"),
    currency: str | None = Query(None, description="Валюта")
):
    return await AnalyticsService(db).summary(date_from, date_to, currency)


@router.get("/transactions")
async def get_transactions(
    db: DBDep,
    pagination: PaginationDep,
    status: str | None = Query(None, description="Статус"),
    currency: str | None = Query(None, description="Валюта"),
    date_from: date | None = Query(None, description="Начало периода"),
    date_to: date | None = Query(None, description="Конец периода"),
):
    return await AnalyticsService(db).get_transactions(
        pagination,
        status,
        currency,
        date_from,
        date_to
    )


@router.get("/transactions/{payment_id}")
async def get_transaction(db: DBDep, payment_id: uuid.UUID):
    try:
        return await AnalyticsService(db).get_transaction(payment_id)
    except TransactionNotFoundException as ex:
        raise TransactionNotFoundHTTPException from ex
