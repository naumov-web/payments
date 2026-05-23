from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.event import (
    EventModel,
)


class TransactionQueryRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self._session = session

    async def get_transaction_by_id(
        self,
        transaction_id: UUID,
    ) -> EventModel | None:
        query = (
            select(EventModel)
            .where(
                EventModel.aggregate_id
                == transaction_id
            )
            .where(
                EventModel.aggregate_type
                == "TRANSACTION"
            )
            .order_by(
                EventModel.stream_version.asc()
            )
        )

        result = await self._session.execute(
            query,
        )

        return result.scalars().first()

    async def has_refund_for_transaction(
        self,
        transaction_id: UUID,
    ) -> bool:
        query = (
            select(EventModel)
            .where(
                EventModel.aggregate_type
                == "TRANSACTION"
            )
            .where(
                EventModel.event_type
                == "TransactionCreated"
            )
            .where(
                EventModel.payload[
                    "transaction_type"
                ].astext
                == "TRANSFER_REFUND"
            )
            .where(
                EventModel.payload[
                    "reference_transaction_id"
                ].astext
                == str(transaction_id)
            )
        )

        result = await self._session.execute(
            query,
        )

        model = result.scalar_one_or_none()

        return model is not None