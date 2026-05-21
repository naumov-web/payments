from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from app.infrastructure.database.engine import engine
from app.infrastructure.event_store.store import EventStore
from app.infrastructure.repositories.actor_aggregate_repository import (
    ActorAggregateRepository,
)
from app.infrastructure.repositories.actor_repository import (
    ActorRepository,
)
from app.infrastructure.repositories.transaction_aggregate_repository import (
    TransactionAggregateRepository,
)
from app.infrastructure.repositories.wallet_balance_repository import (
    WalletBalanceRepository,
)
from app.infrastructure.repositories.ledger_repository import (
    LedgerRepository,
)

class UnitOfWork:
    def __init__(self):
        self._session_factory = async_sessionmaker(
            bind=engine,
            expire_on_commit=False,
        )

        self.session: AsyncSession | None = None
        self.event_store: EventStore | None = None
        self.actor_aggregates: ActorAggregateRepository | None = None
        self.actors: ActorRepository | None = None
        self.transaction_aggregates: TransactionAggregateRepository | None = None
        self.wallet_balances: WalletBalanceRepository | None = None
        self.ledger: LedgerRepository | None = None

    async def __aenter__(self):
        self.session = self._session_factory()
        self.event_store = EventStore(self.session)
        self.actor_aggregates = ActorAggregateRepository(self.event_store)
        self.transaction_aggregates = TransactionAggregateRepository(self.event_store)
        self.wallet_balances = WalletBalanceRepository(self.session)
        self.ledger = LedgerRepository(self.session)
        self.actors = ActorRepository(self.session)

        return self

    async def __aexit__(
        self,
        exc_type,
        exc,
        tb,
    ):
        if exc:
            await self.session.rollback()
        else:
            await self.session.commit()

        await self.session.close()