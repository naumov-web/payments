from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.infrastructure.database.models.actor import (
    ActorModel,
)
from app.infrastructure.database.models.subscription import (
    SubscriptionModel,
)


class SubscriptionDetailsRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self._session = session

    async def get_by_id(
        self,
        subscription_id: UUID,
    ) -> dict | None:
        subscriber = aliased(
            ActorModel,
        )

        service = aliased(
            ActorModel,
        )

        query = (
            select(
                SubscriptionModel,
                subscriber.full_name.label(
                    "subscriber_name",
                ),
                service.full_name.label(
                    "service_name",
                ),
            )
            .join(
                subscriber,
                SubscriptionModel.subscriber_actor_id
                == subscriber.actor_id,
            )
            .join(
                service,
                SubscriptionModel.service_actor_id
                == service.actor_id,
            )
            .where(
                SubscriptionModel.subscription_id
                == subscription_id,
            )
        )

        result = await self._session.execute(
            query,
        )

        row = result.first()

        if row is None:
            return None

        return {
            "subscription": (
                row.SubscriptionModel
            ),
            "subscriber_name": (
                row.subscriber_name
            ),
            "service_name": (
                row.service_name
            ),
        }