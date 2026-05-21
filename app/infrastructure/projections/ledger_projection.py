from app.domain.events.transaction import (
    TransactionCreated,
)
from app.infrastructure.repositories.ledger_repository import (
    LedgerRepository,
)


class LedgerProjectionUpdater:
    def __init__(
        self,
        repository: LedgerRepository,
    ):
        self._repository = repository

    async def apply_transaction_created(
        self,
        event: TransactionCreated,
    ) -> None:
        for entry in event.entries:
            await self._repository.add_entry(
                transaction_id=event.aggregate_id,
                actor_id=entry.actor_id,
                amount=entry.amount,
                transaction_type=(
                    event.transaction_type
                ),
            )