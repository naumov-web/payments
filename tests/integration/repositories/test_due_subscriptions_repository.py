import pytest

from datetime import (
    UTC,
    datetime,
    timedelta,
)
from uuid import uuid4

from app.domain.subscriptions.billing_period import BillingPeriod
from app.domain.subscriptions.subscription_status import SubscriptionStatus
from app.infrastructure.database.models.actor import ActorModel
from app.infrastructure.database.models.subscription import SubscriptionModel
from app.domain.actors.actor_type import ActorType

@pytest.mark.asyncio
async def test_due_subscriptions_repository_returns_active_due_subscription(uow):
    now = datetime.now(UTC)

    subscriber_id = uuid4()
    service_id = uuid4()
    subscription_id = uuid4()

    async with uow as tx:
        tx.session.add(
            ActorModel(
                actor_id=subscriber_id,
                actor_type=ActorType.USER,
            )
        )

        tx.session.add(
            ActorModel(
                actor_id=service_id,
                actor_type=ActorType.SERVICE,
            )
        )

        await tx.subscriptions.create(
            SubscriptionModel(
                subscription_id=subscription_id,
                subscriber_actor_id=subscriber_id,
                service_actor_id=service_id,
                amount=1000,
                billing_period=BillingPeriod.MONTHLY.value,
                status=SubscriptionStatus.ACTIVE.value,
                next_billing_at=now - timedelta(days=1),
                retry_after=None,
            )
        )

    async with uow as tx:
        subscriptions = await tx.due_subscriptions.get_due_subscriptions(
            now=now,
            limit=100,
        )

    assert len(subscriptions) == 1
    assert subscriptions[0].subscription_id == subscription_id

@pytest.mark.asyncio
async def test_due_subscriptions_repository_skips_future_subscription(uow):
    now = datetime.now(UTC)

    subscriber_id = uuid4()
    service_id = uuid4()
    subscription_id = uuid4()

    async with uow as tx:
        tx.session.add(
            ActorModel(
                actor_id=subscriber_id,
                actor_type=ActorType.USER,
            )
        )

        tx.session.add(
            ActorModel(
                actor_id=service_id,
                actor_type=ActorType.SERVICE,
            )
        )

        await tx.subscriptions.create(
            SubscriptionModel(
                subscription_id=subscription_id,
                subscriber_actor_id=subscriber_id,
                service_actor_id=service_id,
                amount=1000,
                billing_period=BillingPeriod.MONTHLY.value,
                status=SubscriptionStatus.ACTIVE.value,
                next_billing_at=(now + timedelta(days=1)),
                retry_after=None,
            )
        )

    async with uow as tx:
        subscriptions = await tx.due_subscriptions.get_due_subscriptions(
            now=now,
            limit=100,
        )

    assert subscriptions == []

@pytest.mark.asyncio
async def test_due_subscriptions_repository_returns_past_due_with_expired_retry(uow):
    now = datetime.now(UTC)

    subscriber_id = uuid4()
    service_id = uuid4()
    subscription_id = uuid4()

    async with uow as tx:
        tx.session.add(
            ActorModel(
                actor_id=subscriber_id,
                actor_type=ActorType.USER,
            )
        )

        tx.session.add(
            ActorModel(
                actor_id=service_id,
                actor_type=ActorType.SERVICE,
            )
        )

        await tx.subscriptions.create(
            SubscriptionModel(
                subscription_id=subscription_id,
                subscriber_actor_id=subscriber_id,
                service_actor_id=service_id,
                amount=1000,
                billing_period=BillingPeriod.MONTHLY.value,
                status=SubscriptionStatus.PAST_DUE.value,
                next_billing_at=(now - timedelta(days=7)),
                retry_after=(now - timedelta(hours=1)),
            )
        )

    async with uow as tx:
        subscriptions = await tx.due_subscriptions.get_due_subscriptions(
            now=now,
            limit=100,
        )

    assert len(subscriptions) == 1
    assert subscriptions[0].subscription_id == subscription_id

@pytest.mark.asyncio
async def test_due_subscriptions_repository_skips_past_due_with_future_retry(uow):
    now = datetime.now(UTC)

    subscriber_id = uuid4()
    service_id = uuid4()
    subscription_id = uuid4()

    async with uow as tx:
        tx.session.add(
            ActorModel(
                actor_id=subscriber_id,
                actor_type=ActorType.USER,
            )
        )

        tx.session.add(
            ActorModel(
                actor_id=service_id,
                actor_type=ActorType.SERVICE,
            )
        )

        await tx.subscriptions.create(
            SubscriptionModel(
                subscription_id=subscription_id,
                subscriber_actor_id=subscriber_id,
                service_actor_id=service_id,
                amount=1000,
                billing_period=BillingPeriod.MONTHLY.value,
                status=SubscriptionStatus.PAST_DUE.value,
                next_billing_at=now - timedelta(days=7),
                retry_after=now + timedelta(hours=1),
            )
        )

    async with uow as tx:
        subscriptions = await tx.due_subscriptions.get_due_subscriptions(
            now=now,
            limit=100,
        )

    assert subscriptions == []

@pytest.mark.asyncio
async def test_due_subscriptions_repository_skips_cancelled_subscription(uow):
    now = datetime.now(UTC)

    subscriber_id = uuid4()
    service_id = uuid4()
    subscription_id = uuid4()

    async with uow as tx:
        tx.session.add(
            ActorModel(
                actor_id=subscriber_id,
                actor_type=ActorType.USER,
            )
        )

        tx.session.add(
            ActorModel(
                actor_id=service_id,
                actor_type=ActorType.SERVICE,
            )
        )

        await tx.subscriptions.create(
            SubscriptionModel(
                subscription_id=subscription_id,
                subscriber_actor_id=subscriber_id,
                service_actor_id=service_id,
                amount=1000,
                billing_period=BillingPeriod.MONTHLY.value,
                status=SubscriptionStatus.CANCELLED.value,
                next_billing_at=now - timedelta(days=1),
                retry_after=None,
            )
        )

    async with uow as tx:
        subscriptions = await tx.due_subscriptions.get_due_subscriptions(
            now=now,
            limit=100,
        )

    assert subscriptions == []