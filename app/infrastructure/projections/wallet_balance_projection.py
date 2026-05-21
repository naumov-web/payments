from app.domain.events.transaction import (
    TransactionCreated,
)
from app.infrastructure.repositories.wallet_balance_repository import (
    WalletBalanceRepository,
)


class WalletBalanceProjectionUpdater:
    def __init__(
        self,
        repository: WalletBalanceRepository,
    ):
        self._repository = repository

    async def apply_transaction_created(
        self,
        event: TransactionCreated,
    ) -> None:
        for entry in event.entries:
            current_balance = (
                await self._repository.get_balance(
                    entry.actor_id,
                )
            )

            new_balance = (
                current_balance + entry.amount
            )

            await self._repository.upsert_balance(
                actor_id=entry.actor_id,
                balance=new_balance,
            )