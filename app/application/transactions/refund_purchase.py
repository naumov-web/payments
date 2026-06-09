from datetime import timedelta
from uuid import UUID
from uuid import uuid4

from app.application.common.idempotency import build_transfer_request_hash
from app.domain.events.transaction import TransactionCreated
from app.domain.idempotency.operation_type import OperationType
from app.domain.transactions.aggregate import TransactionAggregate
from app.domain.transactions.transaction_type import TransactionType
from app.infrastructure.event_store.mapper import map_model_to_domain_event
from app.infrastructure.projections.ledger_projection import LedgerProjectionUpdater
from app.infrastructure.projections.transaction_projection import TransactionProjectionUpdater
from app.infrastructure.projections.wallet_balance_projection import WalletBalanceProjectionUpdater
from app.infrastructure.unit_of_work import UnitOfWork
from app.infrastructure.outbox.publisher import OutboxEventPublisher

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

class RefundPurchaseUseCase:
    REFUND_WINDOW = timedelta(hours=24)

    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    async def execute(
        self,
        *,
        transaction_id: UUID,
        idempotency_key: str,
    ) -> dict:
        async with self._uow as uow:
            model = await uow.transaction_queries.get_transaction_by_id(transaction_id)

            if model is None:
                raise TransactionNotFoundError("Transaction not found.")

            event = map_model_to_domain_event(model)

            if not isinstance(event, TransactionCreated):
                raise RefundNotAllowedError("Invalid transaction.")

            if event.transaction_type != "PURCHASE":
                raise RefundNotAllowedError("Only purchases can be refunded.")

            now = (
                model.occurred_at.tzinfo
                and model.occurred_at.now(tz=model.occurred_at.tzinfo)
            ) or model.occurred_at.now()

            if now - model.occurred_at > self.REFUND_WINDOW:
                raise RefundWindowExpiredError("Refund window expired.")

            already_refunded = await uow.transaction_queries.has_refund_for_transaction(
                transaction_id,
            )

            if already_refunded:
                raise RefundAlreadyExistsError("Transaction already refunded.")

            buyer_entry = next(
                entry
                for entry in event.entries
                if entry.amount < 0
            )

            merchant_entry = next(
                entry
                for entry in event.entries
                if entry.amount > 0
            )

            amount = abs(buyer_entry.amount)

            request_hash = build_transfer_request_hash(
                sender_actor_id=merchant_entry.actor_id,
                receiver_actor_id=buyer_entry.actor_id,
                amount=amount,
            )
            existing_key = await uow.idempotency.get_by_key(idempotency_key)

            if existing_key is not None:
                if existing_key.request_hash != request_hash:
                    raise IdempotencyConflictError("Idempotency key already used with different payload.")

                return existing_key.response_payload

            merchant_balance = await uow.wallet_balances.get_balance(merchant_entry.actor_id)

            if merchant_balance < amount:
                raise InsufficientFundsError("Merchant does not have enough balance for refund.")

            refund_transaction_id = uuid4()

            aggregate = TransactionAggregate.create_transfer(
                aggregate_id=refund_transaction_id,
                source_actor_id=merchant_entry.actor_id,
                target_actor_id=buyer_entry.actor_id,
                amount=amount,
                transaction_type=TransactionType.PURCHASE_REFUND,
                reference_transaction_id=transaction_id,
            )

            events = await uow.transaction_aggregates.save(aggregate)
            outbox_publisher = OutboxEventPublisher(repository=uow.outbox)
            await outbox_publisher.publish(events)

            wallet_projection = WalletBalanceProjectionUpdater(repository=uow.wallet_balances)
            ledger_projection = LedgerProjectionUpdater(repository=uow.ledger)
            transaction_projection = TransactionProjectionUpdater(repository=uow.transactions)

            for event in events:
                if isinstance(event, TransactionCreated):
                    await wallet_projection.apply_transaction_created(event)
                    await ledger_projection.apply_transaction_created(event)
                    await transaction_projection.apply_transaction_created(event)

            response_payload = {
                "transaction_id": str(refund_transaction_id)
            }

            await uow.idempotency.save(
                idempotency_key=idempotency_key,
                operation_type=OperationType.PURCHASE_REFUND,
                request_hash=request_hash,
                response_payload=response_payload,
            )

            return response_payload