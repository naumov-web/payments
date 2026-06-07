from datetime import (
    UTC,
    datetime,
    timedelta,
)
from uuid import uuid4

import pytest

from app.domain.subscriptions.billing_period import BillingPeriod
from app.domain.subscriptions.subscription_status import SubscriptionStatus
from app.infrastructure.database.models.actor import ActorModel
from app.infrastructure.database.models.subscription import SubscriptionModel
from app.workers.subscription_billing_worker import SubscriptionBillingWorker

class FakeChargeSubscriptionUseCase:
    called_subscription_ids = []

    def __init__(self, *, uow):
        pass

    async def execute(
        self,
        *,
        subscription_id,
    ):
        self.called_subscription_ids.append(subscription_id)

        return {
            "status": "success",
        }


@pytest.mark.asyncio
async def test_subscription_billing_worker_processes_due_subscription(uow):
    subscriber_id = uuid4()
    service_id = uuid4()
    subscription_id = uuid4()

    FakeChargeSubscriptionUseCase.called_subscription_ids.clear()

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
                amount=1000,
                billing_period=BillingPeriod.MONTHLY.value,
                status=SubscriptionStatus.ACTIVE.value,
                next_billing_at=(
                    datetime.now(UTC)
                    - timedelta(days=1)
                ),
                retry_after=None,
            )
        )

    worker = SubscriptionBillingWorker(
        uow_factory=lambda: uow,
        charge_subscription_use_case_factory=FakeChargeSubscriptionUseCase
    )

    await worker._process_batch()
    assert FakeChargeSubscriptionUseCase.called_subscription_ids == [subscription_id]

@pytest.mark.asyncio
async def test_subscription_billing_worker_skips_when_no_due_subscriptions(uow):
    FakeChargeSubscriptionUseCase.called_subscription_ids.clear()

    worker = SubscriptionBillingWorker(
        uow_factory=lambda: uow,
        charge_subscription_use_case_factory=FakeChargeSubscriptionUseCase,
    )

    await worker._process_batch()
    assert FakeChargeSubscriptionUseCase.called_subscription_ids == []

@pytest.mark.asyncio
async def test_subscription_billing_worker_processes_multiple_due_subscriptions(uow):
    FakeChargeSubscriptionUseCase.called_subscription_ids.clear()

    subscriber_1 = uuid4()
    service_1 = uuid4()
    subscription_1 = uuid4()

    subscriber_2 = uuid4()
    service_2 = uuid4()
    subscription_2 = uuid4()

    subscriber_3 = uuid4()
    service_3 = uuid4()
    subscription_3 = uuid4()

    async with uow as tx:
        tx.session.add_all(
            [
                ActorModel(
                    actor_id=subscriber_1,
                    actor_type="USER",
                ),
                ActorModel(
                    actor_id=service_1,
                    actor_type="SERVICE",
                ),
                ActorModel(
                    actor_id=subscriber_2,
                    actor_type="USER",
                ),
                ActorModel(
                    actor_id=service_2,
                    actor_type="SERVICE",
                ),
                ActorModel(
                    actor_id=subscriber_3,
                    actor_type="USER",
                ),
                ActorModel(
                    actor_id=service_3,
                    actor_type="SERVICE",
                ),
            ]
        )

        await tx.subscriptions.create(
            SubscriptionModel(
                subscription_id=subscription_1,
                subscriber_actor_id=subscriber_1,
                service_actor_id=service_1,
                amount=1000,
                billing_period=BillingPeriod.MONTHLY.value,
                status=SubscriptionStatus.ACTIVE.value,
                next_billing_at=datetime.now(UTC) - timedelta(days=1),
                retry_after=None,
            )
        )

        await tx.subscriptions.create(
            SubscriptionModel(
                subscription_id=subscription_2,
                subscriber_actor_id=subscriber_2,
                service_actor_id=service_2,
                amount=1000,
                billing_period=BillingPeriod.MONTHLY.value,
                status=SubscriptionStatus.ACTIVE.value,
                next_billing_at=datetime.now(UTC) - timedelta(days=1),
                retry_after=None,
            )
        )

        await tx.subscriptions.create(
            SubscriptionModel(
                subscription_id=subscription_3,
                subscriber_actor_id=subscriber_3,
                service_actor_id=service_3,
                amount=1000,
                billing_period=BillingPeriod.MONTHLY.value,
                status=SubscriptionStatus.ACTIVE.value,
                next_billing_at=datetime.now(UTC) - timedelta(days=1),
                retry_after=None,
            )
        )

    worker = SubscriptionBillingWorker(
        uow_factory=lambda: uow,
        charge_subscription_use_case_factory=FakeChargeSubscriptionUseCase,
    )

    await worker._process_batch()

    assert set(
        FakeChargeSubscriptionUseCase.called_subscription_ids
    ) == {
        subscription_1,
        subscription_2,
        subscription_3,
    }

    assert len(FakeChargeSubscriptionUseCase.called_subscription_ids) == 3

@pytest.mark.asyncio
async def test_subscription_billing_worker_ignores_insufficient_funds_error(uow):
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
                amount=1000,
                billing_period=BillingPeriod.MONTHLY.value,
                status=SubscriptionStatus.ACTIVE.value,
                next_billing_at=datetime.now(UTC) - timedelta(days=1),
                retry_after=None,
            )
        )

    worker = SubscriptionBillingWorker(
        uow_factory=lambda: uow,
        charge_subscription_use_case_factory=FakeChargeSubscriptionUseCase,
    )

    await worker._process_batch()