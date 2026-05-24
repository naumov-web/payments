from uuid import UUID

from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.infrastructure.database.models.actor import (
    ActorModel,
)
from app.infrastructure.database.models.transaction import (
    TransactionModel,
)


class TransactionHistoryRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self._session = session

    async def get_actor_transactions(
        self,
        *,
        actor_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        sender_actor = aliased(
            ActorModel,
        )

        receiver_actor = aliased(
            ActorModel,
        )

        filters = or_(
            TransactionModel.sender_actor_id
            == actor_id,
            TransactionModel.receiver_actor_id
            == actor_id,
        )

        count_query = select(
            func.count()
        ).where(filters)

        total_count_result = (
            await self._session.execute(
                count_query,
            )
        )

        total_count = (
            total_count_result.scalar_one()
        )

        query = (
            select(
                TransactionModel,
                sender_actor.full_name.label(
                    "sender_name"
                ),
                receiver_actor.full_name.label(
                    "receiver_name"
                ),
            )
            .join(
                sender_actor,
                TransactionModel.sender_actor_id
                == sender_actor.actor_id,
            )
            .join(
                receiver_actor,
                TransactionModel.receiver_actor_id
                == receiver_actor.actor_id,
            )
            .where(filters)
            .order_by(
                desc(
                    TransactionModel.created_at
                )
            )
            .limit(limit)
            .offset(offset)
        )

        result = await self._session.execute(
            query,
        )

        rows = result.all()

        items: list[dict] = []

        for row in rows:
            items.append(
                {
                    "transaction": (
                        row.TransactionModel
                    ),
                    "sender_name": (
                        row.sender_name
                    ),
                    "receiver_name": (
                        row.receiver_name
                    ),
                }
            )

        return {
            "total_count": total_count,
            "items": items,
        }