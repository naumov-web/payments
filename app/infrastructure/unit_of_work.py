from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from app.infrastructure.database.engine import engine
from app.infrastructure.event_store.repository import EventStoreRepository
from app.infrastructure.repositories.actor_repository import (
    ActorRepository,
)


class UnitOfWork:
    def __init__(self):
        self._session_factory = async_sessionmaker(
            bind=engine,
            expire_on_commit=False,
        )

        self.session: AsyncSession | None = None

        self.event_store_repository: EventStoreRepository | None = None
        self.actors: ActorRepository | None = None

    async def __aenter__(self):
        self.session = self._session_factory()

        self.event_store_repository = EventStoreRepository(self.session)

        self.actors = ActorRepository(self.session)

        return self

    async def __aexit__(
        self,
        exc_type,
        exc,
        tb,
    ):
        if exc:
            await self.session.rollback()
        else:
            await self.session.commit()

        await self.session.close()