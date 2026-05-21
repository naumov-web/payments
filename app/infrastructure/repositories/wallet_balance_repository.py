from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.wallet_balance import (
    WalletBalanceModel,
)


class WalletBalanceRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self._session = session

    async def get_balance(
        self,
        actor_id: UUID,
    ) -> int:
        query = (
            select(WalletBalanceModel)
            .where(
                WalletBalanceModel.actor_id
                == actor_id
            )
        )

        result = await self._session.execute(
            query,
        )

        model = result.scalar_one_or_none()

        if model is None:
            return 0

        return model.balance

    async def upsert_balance(
        self,
        *,
        actor_id: UUID,
        balance: int,
    ) -> None:
        model = await self._session.get(
            WalletBalanceModel,
            actor_id,
        )

        if model is None:
            model = WalletBalanceModel(
                actor_id=actor_id,
                balance=balance,
            )

            self._session.add(model)

            return

        model.balance = balance