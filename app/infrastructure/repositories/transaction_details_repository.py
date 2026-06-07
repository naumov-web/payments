from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.infrastructure.database.models.actor import (
    ActorModel,
)
from app.infrastructure.database.models.transaction import (
    TransactionModel,
)


class TransactionDetailsRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_transaction_id(self, transaction_id: UUID) -> dict | None:
        sender_actor = aliased(ActorModel)
        receiver_actor = aliased(ActorModel)

        query = (
            select(
                TransactionModel,
                sender_actor.full_name.label("sender_name"),
                receiver_actor.full_name.label("receiver_name"),
            )
            .join(
                sender_actor,
                TransactionModel.sender_actor_id == sender_actor.actor_id,
            )
            .join(
                receiver_actor,
                TransactionModel.receiver_actor_id == receiver_actor.actor_id,
            )
            .where(TransactionModel.transaction_id == transaction_id)
        )

        result = await self._session.execute(query)
        row = result.first()

        if row is None:
            return None

        return {
            "transaction": row.TransactionModel,
            "sender_name": row.sender_name,
            "receiver_name": row.receiver_name,
        }