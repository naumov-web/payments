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
from app.infrastructure.projections.wallet_balance_projection import (
    WalletBalanceProjectionUpdater,
)
from app.infrastructure.projections.transaction_projection import TransactionProjectionUpdater
from app.infrastructure.unit_of_work import (
    UnitOfWork,
)


class ActorNotFoundError(Exception):
    pass


class InsufficientFundsError(Exception):
    pass


class InvalidTransferError(Exception):
    pass


class IdempotencyConflictError(Exception):
    pass


class TransferUseCase:
    def __init__(
        self,
        *,
        uow: UnitOfWork,
    ):
        self._uow = uow

    async def execute(
        self,
        *,
        sender_actor_id: UUID,
        receiver_actor_id: UUID,
        amount: int,
        idempotency_key: str,
    ) -> dict:
        if amount <= 0:
            raise InvalidTransferError(
                "Amount must be positive."
            )

        if (
            sender_actor_id
            == receiver_actor_id
        ):
            raise InvalidTransferError(
                "Sender and receiver "
                "must be different."
            )

        request_hash = (
            build_transfer_request_hash(
                sender_actor_id=(
                    sender_actor_id
                ),
                receiver_actor_id=(
                    receiver_actor_id
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

                return (
                    existing_key.response_payload
                )

            sender = (
                await uow.actors.get_by_id(
                    sender_actor_id,
                )
            )

            if sender is None:
                raise ActorNotFoundError(
                    "Sender actor not found."
                )

            receiver = (
                await uow.actors.get_by_id(
                    receiver_actor_id,
                )
            )

            if receiver is None:
                raise ActorNotFoundError(
                    "Receiver actor not found."
                )

            sender_balance = (
                await (
                    uow.wallet_balances.get_balance(
                        sender_actor_id,
                    )
                )
            )

            if sender_balance < amount:
                raise (
                    InsufficientFundsError(
                        "Insufficient funds."
                    )
                )

            transaction_id = uuid4()

            aggregate = (
                TransactionAggregate.create_transfer(
                    aggregate_id=transaction_id,
                    source_actor_id=(
                        sender_actor_id
                    ),
                    target_actor_id=(
                        receiver_actor_id
                    ),
                    amount=amount,
                )
            )

            events = (
                await (
                    uow.transaction_aggregates.save(
                        aggregate,
                    )
                )
            )

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

            response_payload = {
                "transaction_id": str(
                    transaction_id
                )
            }

            await uow.idempotency.save(
                idempotency_key=(
                    idempotency_key
                ),
                operation_type="TRANSFER",
                request_hash=request_hash,
                response_payload=(
                    response_payload
                ),
            )

            return response_payload