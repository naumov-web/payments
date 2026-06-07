from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.idempotency_key import (
    IdempotencyKeyModel,
)


class IdempotencyRepository:
    def __init__(self,session: AsyncSession):
        self._session = session

    async def get_by_key(self, idempotency_key: str) -> IdempotencyKeyModel | None:
        query = (
            select(IdempotencyKeyModel)
            .where(IdempotencyKeyModel.idempotency_key == idempotency_key)
        )

        result = await self._session.execute(query)

        return result.scalar_one_or_none()

    async def save(
        self,
        *,
        idempotency_key: str,
        operation_type: str,
        request_hash: str,
        response_payload: dict,
    ) -> None:
        model = IdempotencyKeyModel(
            idempotency_key=idempotency_key,
            operation_type=operation_type,
            request_hash=request_hash,
            response_payload=response_payload,
        )

        self._session.add(model)