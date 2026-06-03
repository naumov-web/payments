from datetime import (
    UTC,
    datetime,
    timedelta,
)
from uuid import (
    uuid4,
)

import pytest

from app.application.subscriptions.cancel_subscription import (
    CancelSubscriptionUseCase,
    SubscriptionNotFoundError,
    SubscriptionAlreadyCancelledError,
)
from app.domain.subscriptions.billing_period import (
    BillingPeriod,
)
from app.domain.subscriptions.subscription_status import (
    SubscriptionStatus,
)
from app.infrastructure.database.models.actor import (
    ActorModel,
)
from app.infrastructure.database.models.subscription import (
    SubscriptionModel,
)


@pytest.mark.asyncio
async def test_cancel_subscription_success(
    uow,
):
    subscriber_id = uuid4()
    service_id = uuid4()
    subscription_id = uuid4()

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

        await tx.subscriptions.create(
            SubscriptionModel(
                subscription_id=subscription_id,
                subscriber_actor_id=subscriber_id,
                service_actor_id=service_id,
                amount=1_000,
                billing_period=BillingPeriod.MONTHLY,
                status=SubscriptionStatus.ACTIVE,
                next_billing_at=(
                    datetime.now(UTC)
                    + timedelta(days=30)
                ),
                retry_after=None,
            )
        )

    use_case = CancelSubscriptionUseCase(
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
            == SubscriptionStatus.CANCELLED
        )

@pytest.mark.asyncio
async def test_cancel_subscription_not_found(
    uow,
):
    use_case = CancelSubscriptionUseCase(
        uow=uow,
    )

    with pytest.raises(
        SubscriptionNotFoundError,
        match="Subscription not found.",
    ):
        await use_case.execute(
            subscription_id=uuid4(),
        )

@pytest.mark.asyncio
async def test_cancel_subscription_already_cancelled(
    uow,
):
    subscriber_id = uuid4()
    service_id = uuid4()
    subscription_id = uuid4()

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

        await tx.subscriptions.create(
            SubscriptionModel(
                subscription_id=subscription_id,
                subscriber_actor_id=subscriber_id,
                service_actor_id=service_id,
                amount=1_000,
                billing_period=BillingPeriod.MONTHLY,
                status=SubscriptionStatus.CANCELLED,
                next_billing_at=(
                    datetime.now(UTC)
                    + timedelta(days=30)
                ),
                retry_after=None,
            )
        )

    use_case = CancelSubscriptionUseCase(
        uow=uow,
    )

    with pytest.raises(
        SubscriptionAlreadyCancelledError,
        match="Subscription already cancelled.",
    ):
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
            == SubscriptionStatus.CANCELLED
        )