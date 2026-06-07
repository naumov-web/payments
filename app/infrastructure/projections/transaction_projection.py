from app.domain.events.transaction import TransactionCreated
from app.infrastructure.repositories.transaction_repository import TransactionRepository

class TransactionProjectionUpdater:
    def __init__(self, repository: TransactionRepository):
        self._repository = repository

    async def apply_transaction_created(self, event: TransactionCreated) -> None:
        sender_entry = next(
            entry
            for entry in event.entries
            if entry.amount < 0
        )

        receiver_entry = next(
            entry
            for entry in event.entries
            if entry.amount > 0
        )

        amount = abs(sender_entry.amount)

        await self._repository.save(
            transaction_id=event.aggregate_id,
            transaction_type=event.transaction_type,
            sender_actor_id=sender_entry.actor_id,
            receiver_actor_id=receiver_entry.actor_id,
            amount=amount,
            reference_transaction_id=event.reference_transaction_id,
            created_at=event.occurred_at,
        )