from typing import Annotated

from fastapi import Depends

from app.core.config import settings
from app.core.database import async_session_maker
from app.integrations.payment_provider_client import PaymentProviderClient
from app.services.db_manager import DBManager


async def get_db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]


def get_payment_provider():
    return PaymentProviderClient(base_url=settings.PROVIDER_URL)


PaymentsProviderDep = Annotated[PaymentProviderClient, Depends(get_payment_provider)]
