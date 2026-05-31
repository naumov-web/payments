import asyncio
from datetime import UTC
from datetime import datetime

from app.application.subscriptions.charge_subscription import (
    ChargeSubscriptionUseCase,
    InsufficientFundsError
)
from app.infrastructure.unit_of_work import UnitOfWork

class SubscriptionBillingWorker:
    POLL_INTERVAL_SECONDS = 60

    async def run(self) -> None:
        while True:
            try:
                await self._process_batch()

            except Exception:
                pass

            await asyncio.sleep(self.POLL_INTERVAL_SECONDS)

    async def _process_batch(
        self,
    ) -> None:
        async with UnitOfWork() as uow:
            subscriptions = await uow.due_subscriptions.get_due_subscriptions(
                now=datetime.now(UTC),
                limit=100,
            )

        for subscription in subscriptions:
            await self._process_subscription(subscription.subscription_id)

    async def _process_subscription(self, subscription_id) -> None:
        use_case = ChargeSubscriptionUseCase(uow=UnitOfWork())

        try:
            await use_case.execute(subscription_id=subscription_id)

        except InsufficientFundsError:
            pass

        except Exception:
            raise