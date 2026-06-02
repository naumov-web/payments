from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.infrastructure.database.engine import engine
from app.infrastructure.event_store.store import EventStore
from app.infrastructure.repositories.actor_aggregate_repository import ActorAggregateRepository
from app.infrastructure.repositories.actor_repository import ActorRepository
from app.infrastructure.repositories.transaction_aggregate_repository import TransactionAggregateRepository
from app.infrastructure.repositories.wallet_balance_repository import WalletBalanceRepository
from app.infrastructure.repositories.ledger_repository import LedgerRepository
from app.infrastructure.repositories.idempotency_repository import IdempotencyRepository
from app.infrastructure.repositories.transaction_query_repository import TransactionQueryRepository
from app.infrastructure.repositories.transaction_repository import TransactionRepository
from app.infrastructure.repositories.transaction_history_repository import TransactionHistoryRepository
from app.infrastructure.repositories.transaction_details_repository import TransactionDetailsRepository
from app.infrastructure.repositories.actor_details_repository import ActorDetailsRepository
from app.infrastructure.repositories.outbox_repository import OutboxRepository
from app.infrastructure.repositories.subscription_repository import SubscriptionRepository
from app.infrastructure.repositories.due_subscriptions_repository import DueSubscriptionsRepository
from app.infrastructure.repositories.subscription_details_repository import SubscriptionDetailsRepository
from app.infrastructure.repositories.subscription_billing_repository import SubscriptionBillingRepository

class UnitOfWork:
    def __init__(
        self,
        session_factory= None,
    ):
        self._session_factory = (
            session_factory
            or async_sessionmaker(
                bind=engine,
                expire_on_commit=False,
            )
        )

        self.session: AsyncSession | None = None
        self.event_store: EventStore | None = None
        self.actor_aggregates: ActorAggregateRepository | None = None
        self.actors: ActorRepository | None = None
        self.transaction_aggregates: TransactionAggregateRepository | None = None
        self.wallet_balances: WalletBalanceRepository | None = None
        self.ledger: LedgerRepository | None = None
        self.idempotency: IdempotencyRepository | None = None
        self.transaction_queries: TransactionQueryRepository | None = None
        self.transactions: TransactionRepository | None = None
        self.transaction_history: TransactionHistoryRepository | None = None
        self.transaction_details: TransactionDetailsRepository | None = None
        self.actor_details: ActorDetailsRepository | None = None
        self.outbox: OutboxRepository | None = None
        self.subscriptions: SubscriptionRepository | None = None
        self.due_subscriptions: DueSubscriptionsRepository | None = None
        self.subscription_details: SubscriptionDetailsRepository | None = None
        self.subscription_billing: SubscriptionBillingRepository | None = None

    async def __aenter__(self):
        self.session = self._session_factory()
        self.event_store = EventStore(self.session)
        self.actor_aggregates = ActorAggregateRepository(self.event_store)
        self.transaction_aggregates = TransactionAggregateRepository(self.event_store)
        self.wallet_balances = WalletBalanceRepository(self.session)
        self.ledger = LedgerRepository(self.session)
        self.actors = ActorRepository(self.session)
        self.idempotency = IdempotencyRepository(self.session)
        self.transaction_queries = TransactionQueryRepository(self.session)
        self.transactions = TransactionRepository(self.session)
        self.transaction_history = TransactionHistoryRepository(self.session)
        self.transaction_details = TransactionDetailsRepository(self.session)
        self.actor_details = ActorDetailsRepository(self.session)
        self.outbox = OutboxRepository(self.session)
        self.subscriptions = SubscriptionRepository(self.session)
        self.due_subscriptions = DueSubscriptionsRepository(self.session)
        self.subscription_details = SubscriptionDetailsRepository(self.session)
        self.subscription_billing = SubscriptionBillingRepository(self.session)

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