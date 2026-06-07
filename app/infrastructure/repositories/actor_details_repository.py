from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.actor import ActorModel
from app.infrastructure.database.models.wallet_balance import WalletBalanceModel

class ActorDetailsRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_actor_id(self, actor_id: UUID) -> dict | None:
        query = (
            select(ActorModel, WalletBalanceModel.balance)
            .outerjoin(
                WalletBalanceModel,
                ActorModel.actor_id == WalletBalanceModel.actor_id,
            )
            .where(ActorModel.actor_id == actor_id)
        )

        result = await self._session.execute(query)
        row = result.first()

        if row is None:
            return None

        return {
            "actor": row.ActorModel,
            "balance": row.balance or 0,
        }