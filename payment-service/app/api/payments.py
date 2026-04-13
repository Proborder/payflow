from uuid import UUID

from fastapi import APIRouter, Response
from starlette import status

from app.api.dependencies import DBDep, PaymentsProviderDep
from app.core.exceptions import (
    PaymentNotFoundException,
    PaymentNotFoundHTTPException,
    DatabaseNotUnavailableException,
    DatabaseNotUnavailableHTTPException,
)
from app.schemas.payments import PaymentCreateRequest, PaymentResponse
from app.services.payments import PaymentsService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(db: DBDep, payment_id: UUID):
    try:
        return await PaymentsService(db).get_payment(payment_id)
    except PaymentNotFoundException as ex:
        raise PaymentNotFoundHTTPException from ex
    except DatabaseNotUnavailableException as ex:
        raise DatabaseNotUnavailableHTTPException from ex


@router.post("", response_model=PaymentResponse)
async def create_payment(
    db: DBDep,
    provider: PaymentsProviderDep,
    response: Response,
    payment_data: PaymentCreateRequest
) -> PaymentResponse:
    try:
        payment, is_created = await PaymentsService(db).create_payment(payment_data, provider)
        response.status_code = (
            status.HTTP_201_CREATED if is_created else status.HTTP_200_OK
        )
        return payment
    except DatabaseNotUnavailableException as ex:
        raise DatabaseNotUnavailableHTTPException from ex
