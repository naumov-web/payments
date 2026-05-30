from uuid import UUID
from app.domain.subscriptions.subscription_status import SubscriptionStatus
from app.infrastructure.unit_of_work import UnitOfWork

class SubscriptionNotFoundError(Exception):
    pass

class SubscriptionAlreadyCancelledError(Exception):
    pass

class CancelSubscriptionUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    async def execute(self, *, subscription_id: UUID) -> None:
        async with self._uow as uow:
            subscription = await uow.subscriptions.get_by_id(subscription_id)

            if subscription is None:
                raise SubscriptionNotFoundError("Subscription not found.")

            if subscription.status == SubscriptionStatus.CANCELLED:
                raise SubscriptionAlreadyCancelledError("Subscription already cancelled.")

            subscription.status = SubscriptionStatus.CANCELLED