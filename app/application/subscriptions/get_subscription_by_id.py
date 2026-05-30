from uuid import UUID
from app.infrastructure.unit_of_work import UnitOfWork

class SubscriptionNotFoundError(Exception):
    pass

class GetSubscriptionByIdUseCase:
    def __init__(
        self,
        *,
        uow: UnitOfWork,
    ):
        self._uow = uow

    async def execute(
        self,
        *,
        subscription_id: UUID,
    ) -> dict:
        async with self._uow as uow:
            result = await (
                uow.subscription_details.get_by_id(
                    subscription_id,
                )
            )

            if result is None:
                raise SubscriptionNotFoundError(
                    "Subscription not found."
                )

            subscription = result[
                "subscription"
            ]

            return {
                "subscription_id": (
                    subscription.subscription_id
                ),
                "subscriber_actor_id": (
                    subscription.subscriber_actor_id
                ),
                "subscriber_name": (
                    result["subscriber_name"]
                ),
                "service_actor_id": (
                    subscription.service_actor_id
                ),
                "service_name": (
                    result["service_name"]
                ),
                "amount": (
                    subscription.amount
                ),
                "billing_period": (
                    subscription.billing_period
                ),
                "status": (
                    subscription.status
                ),
                "next_billing_at": (
                    subscription.next_billing_at
                ),
                "created_at": (
                    subscription.created_at
                ),
            }