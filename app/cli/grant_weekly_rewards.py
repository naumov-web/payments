import asyncio
from uuid import UUID

from app.application.transactions.grant_weekly_rewards import (
    GrantWeeklyRewardsUseCase,
    InsufficientFundsError,
)
from app.infrastructure.unit_of_work import (
    UnitOfWork,
)

REWARDS_POOL_ACTOR_ID = UUID(
    "00000000-0000-0000-0000-000000000001"
)

async def grant_weekly_rewards():
    use_case = GrantWeeklyRewardsUseCase(
        uow=UnitOfWork(),
        rewards_pool_actor_id=(
            REWARDS_POOL_ACTOR_ID
        ),
    )

    try:
        transaction_ids = (
            await use_case.execute()
        )

    except InsufficientFundsError as exc:
        print(str(exc))
        return

    print(
        "Weekly rewards granted successfully."
    )

    print(
        f"Created {len(transaction_ids)} "
        "transactions."
    )


if __name__ == "__main__":
    asyncio.run(
        grant_weekly_rewards()
    )