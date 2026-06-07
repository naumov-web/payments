import asyncio
import sys
from uuid import UUID

from app.application.transactions.treasury_funding import TreasuryFundingUseCase
from app.infrastructure.unit_of_work import UnitOfWork

TREASURY_ACTOR_ID = UUID("00000000-0000-0000-0000-000000000004")
REWARDS_POOL_ACTOR_ID = UUID("00000000-0000-0000-0000-000000000001")

async def fund_rewards_pool():
    if len(sys.argv) != 2:
        print(
            "Usage: "
            "python -m app.cli.fund_rewards_pool "
            "<amount_in_dollars>"
        )
        return

    amount_input = sys.argv[1]

    amount = int(float(amount_input) * 100)
    use_case = TreasuryFundingUseCase(
        uow=UnitOfWork(),
        treasury_actor_id=TREASURY_ACTOR_ID,
    )

    transaction_id = await use_case.execute(
        target_actor_id=REWARDS_POOL_ACTOR_ID,
        amount=amount,
    )

    print("Rewards pool funded successfully.")
    print(f"Transaction ID: {transaction_id}")

if __name__ == "__main__":
    asyncio.run(fund_rewards_pool())