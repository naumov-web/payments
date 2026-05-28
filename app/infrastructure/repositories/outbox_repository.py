from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.outbox_message import OutboxMessageModel

class OutboxRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self._session = session

    async def add(
        self,
        *,
        topic: str,
        payload: dict,
    ) -> None:
        message = OutboxMessageModel(
            topic=topic,
            payload=payload,
            status="PENDING",
        )

        self._session.add(message)

    async def get_pending(
        self,
        *,
        limit: int = 100,
    ) -> list[OutboxMessageModel]:
        query = (
            select(OutboxMessageModel)
            .where(
                OutboxMessageModel.status
                == "PENDING"
            )
            .order_by(
                OutboxMessageModel.created_at.asc()
            )
            .limit(limit)
        )

        result = await self._session.execute(
            query,
        )

        return list(
            result.scalars().all()
        )

    async def mark_processed(
        self,
        message_id: UUID,
    ) -> None:
        message = await self._session.get(
            OutboxMessageModel,
            message_id,
        )

        if message is None:
            return

        message.status = "PROCESSED"

        message.processed_at = (
            datetime.utcnow()
        )

    async def mark_failed(
        self,
        message_id: UUID,
    ) -> None:
        message = await self._session.get(
            OutboxMessageModel,
            message_id,
        )

        if message is None:
            return

        message.status = "FAILED"