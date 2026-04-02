from typing import Annotated

from fastapi import Depends

from app.core.database import async_session_maker
from app.integrations.payment_provider_client import PaymentProviderClient
from app.services.db_manager import DBManager


async def get_db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]


class State:
    payment_client: PaymentProviderClient = None


state = State()


def get_payment_provider():
    return state.payment_client


PaymentsProviderDep = Annotated[PaymentProviderClient, Depends(get_payment_provider)]
