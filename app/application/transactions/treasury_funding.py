from uuid import UUID
from uuid import uuid4

from app.domain.events.transaction import (
    TransactionCreated,
)
from app.domain.transactions.aggregate import (
    TransactionAggregate,
)
from app.infrastructure.projections.wallet_balance_projection import (
    WalletBalanceProjectionUpdater,
)
from app.infrastructure.projections.ledger_projection import (
    LedgerProjectionUpdater,
)
from app.infrastructure.projections.transaction_projection import TransactionProjectionUpdater
from app.infrastructure.unit_of_work import UnitOfWork

class ActorNotFoundError(Exception):
    pass

class TreasuryFundingUseCase:
    def __init__(
        self,
        *,
        uow: UnitOfWork,
        treasury_actor_id: UUID,
    ):
        self._uow = uow

        self._treasury_actor_id = (
            treasury_actor_id
        )

    async def execute(
        self,
        *,
        target_actor_id: UUID,
        amount: int,
    ) -> UUID:
        async with self._uow as uow:
            target_actor = (
                await uow.actors.get_by_id(
                    target_actor_id,
                )
            )

            if target_actor is None:
                raise ActorNotFoundError(
                    "Target actor not found."
                )

            transaction_id = uuid4()

            aggregate = (
                TransactionAggregate.create_reward(
                    aggregate_id=transaction_id,
                    source_actor_id=(
                        self._treasury_actor_id
                    ),
                    target_actor_id=target_actor_id,
                    amount=amount,
                )
            )

            events = (
                await uow.transaction_aggregates.save(
                    aggregate,
                )
            )

            wallet_projection = (
                WalletBalanceProjectionUpdater(
                    repository=uow.wallet_balances,
                )
            )
            ledger_projection = (
                LedgerProjectionUpdater(
                    repository=uow.ledger,
                )
            )
            transaction_projection = (
                TransactionProjectionUpdater(
                    repository=uow.transactions,
                )
            )


            for event in events:
                if isinstance(
                    event,
                    TransactionCreated,
                ):
                    await (
                        wallet_projection.apply_transaction_created(
                            event,
                        )
                    )
                    await (
                        ledger_projection.apply_transaction_created(
                            event,
                        )
                    )
                    await (
                        transaction_projection.apply_transaction_created(
                            event,
                        )
                    )

            return transaction_id