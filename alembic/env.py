from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.config.settings import get_settings
from app.infrastructure.database.base import Base
from app.infrastructure.database.models.event import EventModel
from app.infrastructure.database.models.snapshot import SnapshotModel
from app.infrastructure.database.models.actor import ActorModel
from app.infrastructure.database.models.wallet_balance import WalletBalanceModel
from app.infrastructure.database.models.ledger_entry import LedgerEntryModel
from app.infrastructure.database.models.idempotency_key import IdempotencyKeyModel
from app.infrastructure.database.models.transaction import TransactionModel
from app.infrastructure.database.models.outbox_message import OutboxMessageModel

# Alembic Config object
config = context.config

# Logging configuration
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import your metadata here later
# from app.infrastructure.database.models import Base
# target_metadata = Base.metadata

target_metadata = Base.metadata

# Load application settings
settings = get_settings()

# Replace async driver for migrations
DATABASE_URL = settings.postgres_dsn.replace(
    "postgresql+asyncpg",
    "postgresql+psycopg",
)

config.set_main_option("sqlalchemy.url", DATABASE_URL)


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    """

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """
    Run migrations with a live connection.
    """

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio

    asyncio.run(run_migrations_online())