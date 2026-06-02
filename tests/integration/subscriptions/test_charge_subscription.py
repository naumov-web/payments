from datetime import (
    UTC,
    datetime,
    timedelta,
)
from uuid import uuid4

import pytest

from app.application.subscriptions.charge_subscription import (
    ChargeSubscriptionUseCase,
)
from app.domain.subscriptions.billing_period import (
    BillingPeriod,
)
from app.domain.subscriptions.subscription_status import (
    SubscriptionStatus,
)
from app.domain.subscriptions.billing_status import (
    BillingStatus,
)
from app.infrastructure.database.models.actor import (
    ActorModel,
)
from app.infrastructure.database.models.subscription import (
    SubscriptionModel,
)

@pytest.mark.asyncio
async def test_charge_subscription_success(
    uow,
):
    subscriber_id = uuid4()
    service_id = uuid4()
    subscription_id = uuid4()

    billing_date = (
        datetime.now(UTC)
        - timedelta(days=1)
    )

    async with uow as tx:
        tx.session.add(
            ActorModel(
                actor_id=subscriber_id,
                actor_type="USER",
            )
        )

        tx.session.add(
            ActorModel(
                actor_id=service_id,
                actor_type="SERVICE",
            )
        )

        await tx.wallet_balances.upsert_balance(
            actor_id=subscriber_id,
            balance=10_000,
        )

        await tx.wallet_balances.upsert_balance(
            actor_id=service_id,
            balance=0,
        )

        await tx.subscriptions.create(
            SubscriptionModel(
                subscription_id=subscription_id,
                subscriber_actor_id=subscriber_id,
                service_actor_id=service_id,
                amount=1_000,
                billing_period=BillingPeriod.MONTHLY.value,
                status=SubscriptionStatus.ACTIVE.value,
                next_billing_at=billing_date,
                retry_after=None,
            )
        )

    use_case = ChargeSubscriptionUseCase(
        uow=uow,
    )

    await use_case.execute(
        subscription_id=subscription_id,
    )

    async with uow as tx:
        subscription = (
            await tx.subscriptions.get_by_id(
                subscription_id,
            )
        )

        assert subscription is not None

        assert (
            subscription.status
            == SubscriptionStatus.ACTIVE.value
        )

        assert (
            subscription.retry_after
            is None
        )

        assert (
            subscription.next_billing_at
            > billing_date
        )

        billing = (
            await tx.subscription_billing
            .get_by_subscription_and_date(
                subscription_id=subscription_id,
                billing_date=billing_date,
            )
        )

        assert billing is not None

        assert billing.transaction_id is not None

        assert (
            billing.status
            == BillingStatus.SUCCESS.value
        )

        subscriber_balance = (
            await tx.wallet_balances.get_balance(
                subscriber_id,
            )
        )

        service_balance = (
            await tx.wallet_balances.get_balance(
                service_id,
            )
        )

        assert subscriber_balance == 9_000

        assert service_balance == 1_000

@pytest.mark.asyncio
async def test_charge_subscription_insufficient_funds(
    uow,
):
    subscriber_id = uuid4()
    service_id = uuid4()
    subscription_id = uuid4()

    billing_date = (
        datetime.now(UTC)
        - timedelta(days=1)
    )

    async with uow as tx:
        tx.session.add(
            ActorModel(
                actor_id=subscriber_id,
                actor_type="USER",
            )
        )

        tx.session.add(
            ActorModel(
                actor_id=service_id,
                actor_type="SERVICE",
            )
        )

        await tx.wallet_balances.upsert_balance(
            actor_id=subscriber_id,
            balance=500,
        )

        await tx.wallet_balances.upsert_balance(
            actor_id=service_id,
            balance=0,
        )

        await tx.subscriptions.create(
            SubscriptionModel(
                subscription_id=subscription_id,
                subscriber_actor_id=subscriber_id,
                service_actor_id=service_id,
                amount=1_000,
                billing_period=BillingPeriod.MONTHLY.value,
                status=SubscriptionStatus.ACTIVE.value,
                next_billing_at=billing_date,
                retry_after=None,
            )
        )

    use_case = ChargeSubscriptionUseCase(
        uow=uow,
    )

    await use_case.execute(
        subscription_id=subscription_id,
    )

    async with uow as tx:
        subscription = (
            await tx.subscriptions.get_by_id(
                subscription_id,
            )
        )

        assert subscription is not None

        assert (
            subscription.status
            == SubscriptionStatus.PAST_DUE.value
        )

        assert (
            subscription.retry_after
            is not None
        )

        assert (
            subscription.next_billing_at
            == billing_date
        )

        billing = (
            await tx.subscription_billing
            .get_by_subscription_and_date(
                subscription_id=subscription_id,
                billing_date=billing_date,
            )
        )

        assert billing is not None

        assert (
            billing.status
            == BillingStatus.FAILED.value
        )

        subscriber_balance = (
            await tx.wallet_balances.get_balance(
                subscriber_id,
            )
        )

        service_balance = (
            await tx.wallet_balances.get_balance(
                service_id,
            )
        )

        assert subscriber_balance == 500
        assert service_balance == 0