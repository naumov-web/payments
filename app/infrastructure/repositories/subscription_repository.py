from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.subscription import (
    SubscriptionModel,
)
from app.domain.subscriptions.subscription_status import (
    SubscriptionStatus,
)


class SubscriptionRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self._session = session

    async def create(
        self,
        subscription: SubscriptionModel,
    ) -> None:
        self._session.add(subscription)

    async def get_by_id(
        self,
        subscription_id: UUID,
    ) -> SubscriptionModel | None:
        return await self._session.get(
            SubscriptionModel,
            subscription_id,
        )

    async def get_active_subscription(
            self,
            *,
            subscriber_actor_id: UUID,
            service_actor_id: UUID,
    ):
        query = (
            select(
                SubscriptionModel,
            )
            .where(
                SubscriptionModel.subscriber_actor_id
                == subscriber_actor_id,
            )
            .where(
                SubscriptionModel.service_actor_id
                == service_actor_id,
            )
            .where(
                SubscriptionModel.status
                == SubscriptionStatus.ACTIVE,
            )
        )

        result = await self._session.execute(
            query,
        )

        return result.scalar_one_or_none()

