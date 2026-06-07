from datetime import datetime
from uuid import UUID
from sqlalchemy import exists
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.subscription_billing import SubscriptionBillingModel

class SubscriptionBillingRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, billing: SubscriptionBillingModel) -> None:
        self._session.add(billing)

    async def get_by_id(self, billing_id: UUID) -> SubscriptionBillingModel | None:
        return await self._session.get(
            SubscriptionBillingModel,
            billing_id,
        )

    async def get_by_subscription_and_date(
        self,
        *,
        subscription_id: UUID,
        billing_date: datetime,
    ) -> SubscriptionBillingModel | None:
        query = (
            select(SubscriptionBillingModel)
            .where(SubscriptionBillingModel.subscription_id == subscription_id)
            .where(SubscriptionBillingModel.billing_date == billing_date)
        )

        result = await self._session.execute(query)

        return result.scalar_one_or_none()

    async def exists_for_period(
        self,
        *,
        subscription_id: UUID,
        billing_date: datetime,
    ) -> bool:
        query = select(
            exists()
            .where(SubscriptionBillingModel.subscription_id == subscription_id)
            .where(SubscriptionBillingModel.billing_date == billing_date)
        )
        result = await self._session.execute(query)

        return bool(result.scalar())