import json
from typing import AsyncGenerator
from unittest.mock import AsyncMock

import fakeredis
import pytest
from httpx import AsyncClient, ASGITransport

from app.api.dependencies import get_db
from app.core.database import async_session_maker_null_pool, engine_null_pool, Base
from app.core.redis_conn import redis_manager
from app.main import app
from app.schemas.transactions import TransactionCreate
from app.services.db_manager import DBManager
from app.models.transactions import TransactionsOrm
from app.models.processed_events import ProcessedEventsOrm


@pytest.fixture(scope="session", autouse=True)
async def patch_redis_manager():
    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    redis_manager._redis = fake_redis
    redis_manager.connect = AsyncMock()

    yield fake_redis


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

    with open("tests/mock_transactions.json", encoding="utf-8") as file_transactions:
        transactions = json.load(file_transactions)

    transactions = [TransactionCreate.model_validate(transaction) for transaction in transactions]

    async with DBManager(session_factory=async_session_maker_null_pool) as db_:
        await db_.transactions.add_bulk(transactions)
        await db_.commit()


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
