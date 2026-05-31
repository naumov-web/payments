from datetime import datetime

from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

from app.domain.subscriptions.subscription_status import (
    SubscriptionStatus,
)
from app.infrastructure.database.models.subscription import (
    SubscriptionModel,
)


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
                SubscriptionModel,
            )
            .where(
                SubscriptionModel.status.in_(
                    [
                        SubscriptionStatus.ACTIVE,
                        SubscriptionStatus.PAST_DUE,
                    ]
                )
            )
            .where(
                SubscriptionModel.next_billing_at
                <= now,
            )
            .where(
                or_(
                    SubscriptionModel.retry_after.is_(None),
                    SubscriptionModel.retry_after <= now,
                )
            )
            .order_by(
                SubscriptionModel.next_billing_at.asc(),
            )
            .limit(
                limit,
            )
        )

        result = await self._session.execute(
            query,
        )

        return list(
            result.scalars().all(),
        )

    async def count_due_subscriptions(
            self,
            *,
            now: datetime,
    ) -> int:
        query = (
            select(func.count())
            .select_from(SubscriptionModel)
            .where(
                SubscriptionModel.status.in_(
                    [
                        SubscriptionStatus.ACTIVE,
                        SubscriptionStatus.PAST_DUE,
                    ]
                )
            )
            .where(SubscriptionModel.next_billing_at <= now)
            .where(
                or_(
                    SubscriptionModel.retry_after.is_(None),
                    SubscriptionModel.retry_after <= now,
                )
            )
        )

        result = await self._session.execute(query)

        return int(result.scalar_one())