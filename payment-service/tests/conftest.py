from typing import AsyncGenerator

import pytest
from httpx import AsyncClient, ASGITransport

from app.api.dependencies import get_db
from app.core.config import settings
from app.core.database import async_session_maker_null_pool, engine_null_pool, Base
from app.main import app
from app.services.db_manager import DBManager
from app.models.payments import PaymentsOrm
from app.models.outbox import OutboxOrm


async def get_db_null_pool():
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        yield db


@pytest.fixture(scope="function")
async def db() -> AsyncGenerator[DBManager, None]:
    async for db in get_db_null_pool():
        yield db


app.dependency_overrides[get_db] = get_db_null_pool


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
