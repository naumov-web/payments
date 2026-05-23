from app.domain.events.base import (
    DomainEvent,
)
from app.domain.events.transaction import (
    TransactionCreated,
)
from app.domain.transactions.entities import (
    LedgerEntry,
)
from app.domain.transactions.exceptions import (
    UnbalancedTransactionError,
)


class TransactionAggregate:
    def __init__(self):
        self.id = None

        self.transaction_type = None
        self.entries: list[LedgerEntry] = []

        self.version = 0

        self._uncommitted_events: list[
            DomainEvent
        ] = []

    @classmethod
    def create_reward(
        cls,
        *,
        aggregate_id,
        source_actor_id,
        target_actor_id,
        amount: int,
    ) -> "TransactionAggregate":
        if amount <= 0:
            raise ValueError(
                "Amount must be positive."
            )

        entries = [
            LedgerEntry(
                actor_id=source_actor_id,
                amount=-amount,
            ),
            LedgerEntry(
                actor_id=target_actor_id,
                amount=amount,
            ),
        ]

        total = sum(
            entry.amount
            for entry in entries
        )

        if total != 0:
            raise UnbalancedTransactionError(
                "Transaction is not balanced."
            )

        aggregate = cls()

        event = TransactionCreated(
            aggregate_id=aggregate_id,
            transaction_type="REWARD",
            entries=entries,
        )

        aggregate._record_event(event)

        return aggregate

    @classmethod
    def create_transfer(
            cls,
            *,
            aggregate_id,
            source_actor_id,
            target_actor_id,
            amount: int,
            transaction_type: str = "TRANSFER",
            reference_transaction_id=None,
    ) -> "TransactionAggregate":
        if amount <= 0:
            raise ValueError(
                "Amount must be positive."
            )

        entries = [
            LedgerEntry(
                actor_id=source_actor_id,
                amount=-amount,
            ),
            LedgerEntry(
                actor_id=target_actor_id,
                amount=amount,
            ),
        ]

        total = sum(
            entry.amount
            for entry in entries
        )

        if total != 0:
            raise UnbalancedTransactionError(
                "Transaction is not balanced."
            )

        aggregate = cls()

        event = TransactionCreated(
            aggregate_id=aggregate_id,
            transaction_type=transaction_type,
            entries=entries,
            reference_transaction_id=(
                reference_transaction_id
            ),
        )

        aggregate._record_event(event)

        return aggregate

    def apply(
        self,
        event: DomainEvent,
    ) -> None:
        self._apply(event)

        self.version += 1

    def _record_event(
        self,
        event: DomainEvent,
    ) -> None:
        self._apply(event)

        self._uncommitted_events.append(
            event,
        )

    def _apply(
        self,
        event: DomainEvent,
    ) -> None:
        handler_name = (
            f"_apply_{event.event_type}"
        )

        handler = getattr(
            self,
            handler_name,
            None,
        )

        if handler is None:
            raise ValueError(
                f"No handler for {event.event_type}"
            )

        handler(event)

    def _apply_TransactionCreated(
        self,
        event: TransactionCreated,
    ) -> None:
        self.id = event.aggregate_id

        self.transaction_type = (
            event.transaction_type
        )

        self.entries = event.entries

    def pull_events(
        self,
    ) -> list[DomainEvent]:
        events = (
            self._uncommitted_events.copy()
        )

        self._uncommitted_events.clear()

        return events