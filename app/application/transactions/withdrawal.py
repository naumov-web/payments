from uuid import UUID
from uuid import uuid4

from app.application.common.idempotency import (
    build_transfer_request_hash,
)
from app.domain.events.transaction import (
    TransactionCreated,
)
from app.domain.transactions.aggregate import (
    TransactionAggregate,
)
from app.infrastructure.projections.ledger_projection import (
    LedgerProjectionUpdater,
)
from app.infrastructure.projections.transaction_projection import (
    TransactionProjectionUpdater,
)
from app.infrastructure.projections.wallet_balance_projection import (
    WalletBalanceProjectionUpdater,
)
from app.infrastructure.unit_of_work import (
    UnitOfWork,
)
from app.infrastructure.outbox.publisher import OutboxEventPublisher

WITHDRAWAL_SERVICE_ACTOR_ID = UUID(
    "00000000-0000-0000-0000-000000000006"
)


class ActorNotFoundError(Exception):
    pass


class InsufficientFundsError(Exception):
    pass


class InvalidWithdrawalError(Exception):
    pass


class IdempotencyConflictError(Exception):
    pass


class WithdrawalUseCase:
    def __init__(
        self,
        *,
        uow: UnitOfWork,
    ):
        self._uow = uow

    async def execute(
        self,
        *,
        actor_id: UUID,
        amount: int,
        idempotency_key: str,
    ) -> dict:
        if amount <= 0:
            raise InvalidWithdrawalError(
                "Amount must be positive."
            )

        request_hash = (
            build_transfer_request_hash(
                sender_actor_id=actor_id,
                receiver_actor_id=(
                    WITHDRAWAL_SERVICE_ACTOR_ID
                ),
                amount=amount,
            )
        )

        async with self._uow as uow:
            existing_key = (
                await uow.idempotency.get_by_key(
                    idempotency_key,
                )
            )

            if existing_key is not None:
                if (
                    existing_key.request_hash
                    != request_hash
                ):
                    raise (
                        IdempotencyConflictError(
                            "Idempotency key "
                            "already used with "
                            "different payload."
                        )
                    )

                return existing_key.response_payload

            actor = (
                await uow.actors.get_by_id(
                    actor_id,
                )
            )

            if actor is None:
                raise ActorNotFoundError(
                    "Actor not found."
                )

            withdrawal_service = (
                await uow.actors.get_by_id(
                    WITHDRAWAL_SERVICE_ACTOR_ID,
                )
            )

            if withdrawal_service is None:
                raise ActorNotFoundError(
                    "Withdrawal service "
                    "actor not found."
                )

            balance = (
                await (
                    uow.wallet_balances.get_balance(
                        actor_id,
                    )
                )
            )

            if balance < amount:
                raise (
                    InsufficientFundsError(
                        "Insufficient funds."
                    )
                )

            transaction_id = uuid4()

            aggregate = (
                TransactionAggregate.create_transfer(
                    aggregate_id=transaction_id,
                    source_actor_id=actor_id,
                    target_actor_id=(
                        WITHDRAWAL_SERVICE_ACTOR_ID
                    ),
                    amount=amount,
                    transaction_type="WITHDRAWAL",
                )
            )

            events = (
                await (
                    uow.transaction_aggregates.save(
                        aggregate,
                    )
                )
            )
            outbox_publisher = OutboxEventPublisher(repository=uow.outbox)
            await outbox_publisher.publish(events)

            wallet_projection = (
                WalletBalanceProjectionUpdater(
                    repository=(
                        uow.wallet_balances
                    ),
                )
            )

            ledger_projection = (
                LedgerProjectionUpdater(
                    repository=uow.ledger,
                )
            )

            transaction_projection = (
                TransactionProjectionUpdater(
                    repository=(
                        uow.transactions
                    ),
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

            response_payload = {
                "transaction_id": str(
                    transaction_id
                )
            }

            await uow.idempotency.save(
                idempotency_key=(
                    idempotency_key
                ),
                operation_type="WITHDRAWAL",
                request_hash=request_hash,
                response_payload=(
                    response_payload
                ),
            )

            return response_payload