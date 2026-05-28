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

class ActorNotFoundError(Exception):
    pass


class InsufficientFundsError(Exception):
    pass


class InvalidPurchaseError(Exception):
    pass


class IdempotencyConflictError(Exception):
    pass


class PurchaseUseCase:
    def __init__(
        self,
        *,
        uow: UnitOfWork,
    ):
        self._uow = uow

    async def execute(
        self,
        *,
        buyer_actor_id: UUID,
        merchant_actor_id: UUID,
        amount: int,
        idempotency_key: str,
    ) -> dict:
        if amount <= 0:
            raise InvalidPurchaseError(
                "Amount must be positive."
            )

        if (
            buyer_actor_id
            == merchant_actor_id
        ):
            raise InvalidPurchaseError(
                "Buyer and merchant "
                "must be different."
            )

        request_hash = (
            build_transfer_request_hash(
                sender_actor_id=(
                    buyer_actor_id
                ),
                receiver_actor_id=(
                    merchant_actor_id
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

            buyer = (
                await uow.actors.get_by_id(
                    buyer_actor_id,
                )
            )

            if buyer is None:
                raise ActorNotFoundError(
                    "Buyer actor not found."
                )

            merchant = (
                await uow.actors.get_by_id(
                    merchant_actor_id,
                )
            )

            if merchant is None:
                raise ActorNotFoundError(
                    "Merchant actor not found."
                )

            buyer_balance = (
                await (
                    uow.wallet_balances.get_balance(
                        buyer_actor_id,
                    )
                )
            )

            if buyer_balance < amount:
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
                        buyer_actor_id
                    ),
                    target_actor_id=(
                        merchant_actor_id
                    ),
                    amount=amount,
                    transaction_type="PURCHASE",
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
                operation_type="PURCHASE",
                request_hash=request_hash,
                response_payload=(
                    response_payload
                ),
            )

            return response_payload