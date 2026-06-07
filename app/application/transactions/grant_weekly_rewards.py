from uuid import UUID
from uuid import uuid4
from sqlalchemy import select

from app.domain.events.transaction import TransactionCreated
from app.domain.transactions.aggregate import TransactionAggregate
from app.infrastructure.database.models.actor import ActorModel
from app.infrastructure.projections.wallet_balance_projection import WalletBalanceProjectionUpdater
from app.infrastructure.projections.ledger_projection import LedgerProjectionUpdater
from app.infrastructure.projections.transaction_projection import TransactionProjectionUpdater
from app.infrastructure.unit_of_work import UnitOfWork

class InsufficientFundsError(Exception):
    pass

class GrantWeeklyRewardsUseCase:
    REWARD_AMOUNT = 2000  # $20.00

    def __init__(
        self,
        *,
        uow: UnitOfWork,
        rewards_pool_actor_id: UUID,
    ):
        self._uow = uow
        self._rewards_pool_actor_id =rewards_pool_actor_id

    async def execute(self) -> list[UUID]:
        async with self._uow as uow:
            query = select(ActorModel).where(ActorModel.role == "EMPLOYEE")
            result = await uow.session.execute(query)
            employees = result.scalars().all()
            total_amount = len(employees) * self.REWARD_AMOUNT
            rewards_pool_balance = await uow.wallet_balances.get_balance(
                self._rewards_pool_actor_id,
            )

            if rewards_pool_balance < total_amount:
                raise InsufficientFundsError("Insufficient rewards pool balance.")

            wallet_projection = WalletBalanceProjectionUpdater(repository=uow.wallet_balances)
            ledger_projection = LedgerProjectionUpdater(repository=uow.ledger)
            transaction_projection = TransactionProjectionUpdater(repository=uow.transactions)
            transaction_ids: list[UUID] = []

            for employee in employees:
                transaction_id = uuid4()

                aggregate = TransactionAggregate.create_reward(
                    aggregate_id=transaction_id,
                    source_actor_id=self._rewards_pool_actor_id,
                    target_actor_id=employee.actor_id,
                    amount=self.REWARD_AMOUNT,
                )
                events = await uow.transaction_aggregates.save(aggregate)

                for event in events:
                    if isinstance(event, TransactionCreated):
                        await wallet_projection.apply_transaction_created(event)
                        await ledger_projection.apply_transaction_created(event)
                        await transaction_projection.apply_transaction_created(event)

                transaction_ids.append(transaction_id)

            return transaction_ids