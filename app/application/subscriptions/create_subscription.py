from datetime import UTC
from datetime import datetime
from datetime import timedelta
from uuid import uuid4
from sqlalchemy.exc import IntegrityError

from app.infrastructure.database.models.subscription import (
    SubscriptionModel,
)
from app.infrastructure.unit_of_work import (
    UnitOfWork,
)
from app.domain.transactions.aggregate import (
    TransactionAggregate,
)
from app.domain.subscriptions.subscription_status import (
    SubscriptionStatus,
)
from app.domain.subscriptions.billing_period import (
    BillingPeriod,
)
from app.infrastructure.outbox.publisher import OutboxEventPublisher
from app.infrastructure.projections.ledger_projection import (
    LedgerProjectionUpdater,
)
from app.infrastructure.projections.wallet_balance_projection import (
    WalletBalanceProjectionUpdater,
)
from app.infrastructure.projections.transaction_projection import TransactionProjectionUpdater
from app.domain.events.transaction import (
    TransactionCreated,
)

class SubscriptionAlreadyExistsError(
    Exception,
):
    pass


class InvalidSubscriptionError(
    Exception,
):
    pass


class ActorNotFoundError(
    Exception,
):
    pass


class InsufficientFundsError(
    Exception,
):
    pass


class CreateSubscriptionUseCase:
    def __init__(
        self,
        *,
        uow: UnitOfWork,
    ):
        self._uow = uow

    async def execute(
        self,
        *,
        subscriber_actor_id,
        service_actor_id,
        amount: int,
        billing_period: str,
    ) -> dict:
        if amount <= 0:
            raise InvalidSubscriptionError(
                "Amount must be positive."
            )

        async with self._uow as uow:
            subscriber = await (
                uow.actors.get_by_id(
                    subscriber_actor_id,
                )
            )

            if subscriber is None:
                raise ActorNotFoundError(
                    "Subscriber not found."
                )

            service_actor = await (
                uow.actors.get_by_id(
                    service_actor_id,
                )
            )

            if service_actor is None:
                raise ActorNotFoundError(
                    "Service actor not found."
                )

            balance = await (
                uow.wallet_balances.get_balance(
                    subscriber_actor_id,
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
                    source_actor_id=(
                        subscriber_actor_id
                    ),
                    target_actor_id=(
                        service_actor_id
                    ),
                    amount=amount,
                    transaction_type=(
                        "SUBSCRIPTION_PAYMENT"
                    ),
                )
            )

            events = await (
                uow.transaction_aggregates.save(
                    aggregate,
                )
            )

            outbox_publisher = (
                OutboxEventPublisher(
                    repository=uow.outbox,
                )
            )

            await outbox_publisher.publish(
                events,
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

            now = datetime.now(
                UTC,
            )

            if billing_period == BillingPeriod.WEEKLY:
                next_billing_at = (
                    now + timedelta(days=7)
                )
            elif billing_period == BillingPeriod.MONTHLY:
                next_billing_at = (
                    now + timedelta(days=30)
                )
            else:
                raise (
                    InvalidSubscriptionError(
                        "Unsupported billing period."
                    )
                )

            existing_subscription = (
                await uow.subscriptions.get_active_subscription(
                    subscriber_actor_id=subscriber_actor_id,
                    service_actor_id=service_actor_id,
                )
            )

            if existing_subscription is not None:
                raise SubscriptionAlreadyExistsError(
                    "Active subscription already exists."
                )

            subscription = (
                SubscriptionModel(
                    subscription_id=uuid4(),
                    subscriber_actor_id=(
                        subscriber_actor_id
                    ),
                    service_actor_id=(
                        service_actor_id
                    ),
                    amount=amount,
                    billing_period=(
                        billing_period
                    ),
                    status=SubscriptionStatus.ACTIVE,
                    next_billing_at=(
                        next_billing_at
                    ),
                )
            )

            try:
                await uow.subscriptions.create(
                    subscription,
                )
            except IntegrityError:
                raise SubscriptionAlreadyExistsError(
                    "Active subscription already exists."
                )

            return {
                "subscription_id": str(
                    subscription.subscription_id
                ),
                "transaction_id": str(
                    transaction_id
                ),
            }