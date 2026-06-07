from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.actor import ActorModel

class ActorRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, actor: ActorModel) -> None:
        self._session.add(actor)

    async def get_by_id(
        self,
        actor_id: UUID,
    ) -> ActorModel | None:
        query = (
            select(ActorModel)
            .where(ActorModel.actor_id == actor_id)
        )

        result = await self._session.execute(query)

        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> ActorModel | None:
        query = (
            select(ActorModel)
            .where(ActorModel.email == email)
        )

        result = await self._session.execute(query)

        return result.scalar_one_or_none()