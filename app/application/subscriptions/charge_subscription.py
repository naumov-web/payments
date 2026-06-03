from datetime import UTC
from datetime import datetime
from datetime import timedelta
from uuid import UUID
from uuid import uuid4

from app.domain.events.transaction import (
    TransactionCreated,
)
from app.domain.subscriptions.billing_period import (
    BillingPeriod,
)
from app.domain.subscriptions.billing_status import (
    BillingStatus,
)
from app.domain.subscriptions.subscription_status import (
    SubscriptionStatus,
)
from app.domain.transactions.aggregate import (
    TransactionAggregate,
)
from app.infrastructure.database.models.subscription_billing import (
    SubscriptionBillingModel,
)
from app.infrastructure.outbox.publisher import (
    OutboxEventPublisher,
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


class SubscriptionNotFoundError(Exception):
    pass

class SubscriptionAlreadyBilledError(Exception):
    pass

class InsufficientFundsError(Exception):
    pass

class ChargeSubscriptionUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    async def execute(self, *, subscription_id: UUID) -> dict:
        async with self._uow as uow:
            subscription = await uow.subscriptions.get_by_id(subscription_id)

            if subscription is None:
                raise SubscriptionNotFoundError("Subscription not found.")

            already_billed = await (
                uow.subscription_billing
                .exists_for_period(
                    subscription_id=subscription.subscription_id,
                    billing_date=subscription.next_billing_at
                )
            )

            if already_billed:
                raise SubscriptionAlreadyBilledError("Subscription period already billed.")

            balance = await uow.wallet_balances.get_balance(subscription.subscriber_actor_id)

            if balance < subscription.amount:
                billing = SubscriptionBillingModel(
                    billing_id=uuid4(),
                    subscription_id=subscription.subscription_id,
                    billing_date=subscription.next_billing_at,
                    status=BillingStatus.FAILED,
                )

                await uow.subscription_billing.save(billing)
                subscription.status = SubscriptionStatus.PAST_DUE
                subscription.retry_after = (
                    datetime.now(UTC)
                    + timedelta(days=1)
                )

                return {
                    "status": "insufficient_funds",
                }

            transaction_id = uuid4()
            aggregate = TransactionAggregate.create_transfer(
                aggregate_id=transaction_id,
                source_actor_id=subscription.subscriber_actor_id,
                target_actor_id=subscription.service_actor_id,
                amount=subscription.amount,
                transaction_type="SUBSCRIPTION_PAYMENT",
            )

            events = await uow.transaction_aggregates.save(aggregate)
            outbox_publisher = OutboxEventPublisher(repository=uow.outbox)
            await outbox_publisher.publish(events)

            wallet_projection = WalletBalanceProjectionUpdater(repository=uow.wallet_balances)
            ledger_projection = LedgerProjectionUpdater(repository=uow.ledger)
            transaction_projection = TransactionProjectionUpdater(repository=uow.transactions)

            for event in events:
                if isinstance(event, TransactionCreated):
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

            billing = (
                SubscriptionBillingModel(
                    billing_id=uuid4(),
                    subscription_id=(
                        subscription.subscription_id
                    ),
                    transaction_id=(
                        transaction_id
                    ),
                    billing_date=(
                        subscription.next_billing_at
                    ),
                    status=BillingStatus.SUCCESS,
                )
            )

            await uow.subscription_billing.save(billing)

            subscription.status = SubscriptionStatus.ACTIVE
            subscription.retry_after = None

            if (
                subscription.billing_period
                == BillingPeriod.WEEKLY
            ):
                subscription.next_billing_at = (
                    subscription.next_billing_at
                    + timedelta(days=7)
                )

            elif (
                subscription.billing_period
                == BillingPeriod.MONTHLY
            ):
                subscription.next_billing_at = (
                    subscription.next_billing_at
                    + timedelta(days=30)
                )

            return {
                "status": "Success",
                "transaction_id": str(
                    transaction_id
                )
            }