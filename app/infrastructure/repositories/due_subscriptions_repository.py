from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.subscription import SubscriptionModel
from app.domain.subscriptions.subscription_status import SubscriptionStatus

class DueSubscriptionsRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self._session = session

    async def get_due_subscriptions(
        self,
        *,
        now: datetime,
        limit: int = 100,
    ) -> list[SubscriptionModel]:
        query = (
            select(
                SubscriptionModel
            )
            .where(
                SubscriptionModel.status == SubscriptionStatus.ACTIVE
            )
            .where(
                SubscriptionModel.next_billing_at
                <= now
            )
            .order_by(
                SubscriptionModel.next_billing_at.asc()
            )
            .limit(limit)
        )

        result = await self._session.execute(
            query,
        )

        return list(
            result.scalars().all()
        )