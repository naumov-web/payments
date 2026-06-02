import os

os.environ["POSTGRES_DSN"] = (
    "postgresql+asyncpg://"
    "postgres:postgres@postgres_test:5432/"
    "wallet_test"
)
os.environ["REDIS_URL"] = "redis://redis:6379/0"
os.environ["KAFKA_BOOTSTRAP_SERVERS"] = "kafka:9092"

import pytest
import pytest_asyncio

from alembic import command
from alembic.config import Config

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config.settings import (
    get_settings,
)
from app.infrastructure.unit_of_work import (
    UnitOfWork,
)


TEST_DATABASE_URL = (
    "postgresql+asyncpg://"
    "postgres:postgres@postgres_test:5432/"
    "wallet_test"
)


@pytest.fixture(
    scope="session",
    autouse=True,
)
def migrate_database():
    get_settings.cache_clear()
    config = Config("alembic.ini")
    command.downgrade(config, "base")
    command.upgrade(config, "head")

    yield


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        future=True,
    )

    yield engine

    await engine.dispose()


@pytest.fixture
def test_session_factory(
    test_engine,
):
    return async_sessionmaker(
        bind=test_engine,
        expire_on_commit=False,
        autoflush=False,
        class_=AsyncSession,
    )


@pytest_asyncio.fixture
async def db_session(
    test_session_factory,
):
    async with test_session_factory() as session:
        yield session

        await session.rollback()


@pytest.fixture
def uow(
    test_session_factory,
):
    return UnitOfWork(
        session_factory=test_session_factory,
    )