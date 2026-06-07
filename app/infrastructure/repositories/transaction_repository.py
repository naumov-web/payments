from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.models.transaction import TransactionModel


class TransactionRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self._session = session

    async def save(
        self,
        *,
        transaction_id: UUID,
        transaction_type: str,
        sender_actor_id: UUID,
        receiver_actor_id: UUID,
        amount: int,
        reference_transaction_id: UUID | None,
        created_at,
    ) -> None:
        model = TransactionModel(
            transaction_id=transaction_id,
            transaction_type=transaction_type,
            sender_actor_id=sender_actor_id,
            receiver_actor_id=receiver_actor_id,
            amount=amount,
            reference_transaction_id=reference_transaction_id,
            created_at=created_at,
        )

        self._session.add(model)