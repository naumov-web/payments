from datetime import timedelta
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
from app.infrastructure.event_store.mapper import (
    map_model_to_domain_event,
)
from app.infrastructure.projections.ledger_projection import (
    LedgerProjectionUpdater,
)
from app.infrastructure.projections.wallet_balance_projection import (
    WalletBalanceProjectionUpdater,
)
from app.infrastructure.unit_of_work import (
    UnitOfWork,
)


class TransactionNotFoundError(Exception):
    pass


class RefundNotAllowedError(Exception):
    pass


class RefundWindowExpiredError(Exception):
    pass


class RefundAlreadyExistsError(Exception):
    pass


class InsufficientFundsError(Exception):
    pass


class IdempotencyConflictError(Exception):
    pass


class RefundTransferUseCase:
    REFUND_WINDOW = timedelta(
        minutes=10
    )

    def __init__(
        self,
        *,
        uow: UnitOfWork,
    ):
        self._uow = uow

    async def execute(
        self,
        *,
        transaction_id: UUID,
        idempotency_key: str,
    ) -> dict:
        async with self._uow as uow:
            model = await (
                uow.transaction_queries.get_transaction_by_id(
                    transaction_id,
                )
            )

            if model is None:
                raise (
                    TransactionNotFoundError(
                        "Transaction not found."
                    )
                )

            event = map_model_to_domain_event(
                model,
            )

            if not isinstance(
                event,
                TransactionCreated,
            ):
                raise RefundNotAllowedError(
                    "Invalid transaction."
                )

            if (
                event.transaction_type
                != "TRANSFER"
            ):
                raise RefundNotAllowedError(
                    "Only transfers "
                    "can be refunded."
                )

            now = (
                model.occurred_at.tzinfo
                and model.occurred_at.now(
                    tz=model.occurred_at.tzinfo
                )
            ) or model.occurred_at.now()

            if (
                now - model.occurred_at
                > self.REFUND_WINDOW
            ):
                raise (
                    RefundWindowExpiredError(
                        "Refund window expired."
                    )
                )

            already_refunded = await (
                uow.transaction_queries.has_refund_for_transaction(
                    transaction_id,
                )
            )

            if already_refunded:
                raise (
                    RefundAlreadyExistsError(
                        "Transaction already refunded."
                    )
                )

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

            amount = abs(
                sender_entry.amount
            )

            request_hash = (
                build_transfer_request_hash(
                    sender_actor_id=(
                        receiver_entry.actor_id
                    ),
                    receiver_actor_id=(
                        sender_entry.actor_id
                    ),
                    amount=amount,
                )
            )

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

            receiver_balance = (
                await (
                    uow.wallet_balances.get_balance(
                        receiver_entry.actor_id,
                    )
                )
            )

            if receiver_balance < amount:
                raise (
                    InsufficientFundsError(
                        "Receiver does not "
                        "have enough balance "
                        "for refund."
                    )
                )

            refund_transaction_id = (
                uuid4()
            )

            aggregate = (
                TransactionAggregate.create_transfer(
                    aggregate_id=(
                        refund_transaction_id
                    ),
                    source_actor_id=(
                        receiver_entry.actor_id
                    ),
                    target_actor_id=(
                        sender_entry.actor_id
                    ),
                    amount=amount,
                    transaction_type=(
                        "TRANSFER_REFUND"
                    ),
                    reference_transaction_id=(
                        transaction_id
                    ),
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

            response_payload = {
                "transaction_id": str(
                    refund_transaction_id
                )
            }

            await uow.idempotency.save(
                idempotency_key=(
                    idempotency_key
                ),
                operation_type=(
                    "TRANSFER_REFUND"
                ),
                request_hash=request_hash,
                response_payload=(
                    response_payload
                ),
            )

            return response_payload