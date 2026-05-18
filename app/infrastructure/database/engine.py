from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from app.config.settings import get_settings

settings = get_settings()

engine: AsyncEngine = create_async_engine(
    settings.postgres_dsn,
    echo=False,
    pool_pre_ping=True,
)