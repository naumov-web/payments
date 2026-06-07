from uuid import uuid4

import pytest

from datetime import (
    UTC,
    datetime,
    timedelta,
)

from app.infrastructure.database.models.subscription import SubscriptionModel

from app.application.subscriptions.create_subscription import (
    CreateSubscriptionUseCase,
    InsufficientFundsError,
    SubscriptionAlreadyExistsError,
    InvalidSubscriptionError,
    ActorNotFoundError,
)
from app.domain.subscriptions.billing_period import BillingPeriod
from app.domain.subscriptions.subscription_status import SubscriptionStatus
from app.infrastructure.database.models.actor import ActorModel

@pytest.mark.asyncio
async def test_create_subscription_success(uow):
    subscriber_id = uuid4()
    service_id = uuid4()

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

    use_case = CreateSubscriptionUseCase(uow=uow)

    result = await use_case.execute(
        subscriber_actor_id=subscriber_id,
        service_actor_id=service_id,
        amount=1_000,
        billing_period=BillingPeriod.MONTHLY,
    )

    assert result["subscription_id"]
    assert result["transaction_id"]

    async with uow as tx:
        subscription = await tx.subscriptions.get_active_subscription(
            subscriber_actor_id=subscriber_id,
            service_actor_id=service_id,
        )

        assert subscription is not None
        assert subscription.subscriber_actor_id == subscriber_id
        assert subscription.service_actor_id == service_id
        assert subscription.amount == 1_000
        assert subscription.billing_period == BillingPeriod.MONTHLY
        assert subscription.status == SubscriptionStatus.ACTIVE

        subscriber_balance = await tx.wallet_balances.get_balance(subscriber_id)
        service_balance = await tx.wallet_balances.get_balance(service_id)

        assert subscriber_balance == 9_000
        assert service_balance == 1_000

@pytest.mark.asyncio
async def test_create_subscription_insufficient_funds(uow):
    subscriber_id = uuid4()
    service_id = uuid4()

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

    use_case = CreateSubscriptionUseCase(uow=uow)

    with pytest.raises(
        InsufficientFundsError,
        match="Insufficient funds.",
    ):
        await use_case.execute(
            subscriber_actor_id=subscriber_id,
            service_actor_id=service_id,
            amount=1_000,
            billing_period=BillingPeriod.MONTHLY,
        )

    async with uow as tx:
        subscription = await tx.subscriptions.get_active_subscription(
            subscriber_actor_id=subscriber_id,
            service_actor_id=service_id,
        )

        assert subscription is None

        subscriber_balance = await tx.wallet_balances.get_balance(subscriber_id)
        service_balance = await tx.wallet_balances.get_balance(service_id)

        assert subscriber_balance == 500
        assert service_balance == 0

@pytest.mark.asyncio
async def test_create_subscription_already_exists(uow):
    subscriber_id = uuid4()
    service_id = uuid4()

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
                subscription_id=uuid4(),
                subscriber_actor_id=subscriber_id,
                service_actor_id=service_id,
                amount=1_000,
                billing_period=BillingPeriod.MONTHLY,
                status=SubscriptionStatus.ACTIVE,
                next_billing_at=datetime.now(UTC) + timedelta(days=30),
                retry_after=None,
            )
        )

    use_case = CreateSubscriptionUseCase(uow=uow)

    with pytest.raises(
        SubscriptionAlreadyExistsError,
        match="Active subscription already exists.",
    ):
        await use_case.execute(
            subscriber_actor_id=subscriber_id,
            service_actor_id=service_id,
            amount=1_000,
            billing_period=BillingPeriod.MONTHLY,
        )

    async with uow as tx:
        subscription = await tx.subscriptions.get_active_subscription(
            subscriber_actor_id=subscriber_id,
            service_actor_id=service_id,
        )

        assert subscription is not None

        subscriber_balance = await tx.wallet_balances.get_balance(subscriber_id)
        service_balance = await tx.wallet_balances.get_balance(service_id)

        assert subscriber_balance == 10_000
        assert service_balance == 0

@pytest.mark.asyncio
async def test_create_subscription_invalid_amount(uow):
    subscriber_id = uuid4()
    service_id = uuid4()

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

    use_case = CreateSubscriptionUseCase(uow=uow)

    with pytest.raises(
        InvalidSubscriptionError,
        match="Amount must be positive.",
    ):
        await use_case.execute(
            subscriber_actor_id=subscriber_id,
            service_actor_id=service_id,
            amount=0,
            billing_period=BillingPeriod.MONTHLY,
        )

    async with uow as tx:
        subscription = await tx.subscriptions.get_active_subscription(
            subscriber_actor_id=subscriber_id,
            service_actor_id=service_id,
        )

        assert subscription is None

        subscriber_balance = await tx.wallet_balances.get_balance(subscriber_id)
        service_balance = await tx.wallet_balances.get_balance(service_id)

        assert subscriber_balance == 10_000
        assert service_balance == 0

@pytest.mark.asyncio
async def test_create_subscription_subscriber_not_found(uow):
    service_id = uuid4()
    missing_subscriber_id = uuid4()

    async with uow as tx:
        tx.session.add(
            ActorModel(
                actor_id=service_id,
                actor_type="SERVICE",
            )
        )

    use_case = CreateSubscriptionUseCase(uow=uow)

    with pytest.raises(
        ActorNotFoundError,
        match="Subscriber not found.",
    ):
        await use_case.execute(
            subscriber_actor_id=missing_subscriber_id,
            service_actor_id=service_id,
            amount=1_000,
            billing_period=BillingPeriod.MONTHLY,
        )

    async with uow as tx:
        subscription = await tx.subscriptions.get_active_subscription(
            subscriber_actor_id=missing_subscriber_id,
            service_actor_id=service_id,
        )

        assert subscription is None

        service_balance = await tx.wallet_balances.get_balance(service_id)

        assert service_balance == 0

@pytest.mark.asyncio
async def test_create_subscription_service_actor_not_found(uow):
    subscriber_id = uuid4()
    missing_service_id = uuid4()

    async with uow as tx:
        tx.session.add(
            ActorModel(
                actor_id=subscriber_id,
                actor_type="USER",
            )
        )

        await tx.wallet_balances.upsert_balance(
            actor_id=subscriber_id,
            balance=10_000,
        )

    use_case = CreateSubscriptionUseCase(uow=uow)

    with pytest.raises(
        ActorNotFoundError,
        match="Service actor not found.",
    ):
        await use_case.execute(
            subscriber_actor_id=subscriber_id,
            service_actor_id=missing_service_id,
            amount=1_000,
            billing_period=BillingPeriod.MONTHLY,
        )

    async with uow as tx:
        subscription = await tx.subscriptions.get_active_subscription(
            subscriber_actor_id=subscriber_id,
            service_actor_id=missing_service_id,
        )

        assert subscription is None

        subscriber_balance = await tx.wallet_balances.get_balance(subscriber_id)

        assert subscriber_balance == 10_000