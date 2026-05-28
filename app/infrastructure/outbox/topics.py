from app.domain.events.actor import (
    ActorCreated,
)
from app.domain.events.base import DomainEvent
from app.domain.events.transaction import (
    TransactionCreated,
)


def build_outbox_topic(
    event: DomainEvent,
) -> str:
    if isinstance(
        event,
        TransactionCreated,
    ):
        return (
            "transactions.created"
        )

    if isinstance(
        event,
        ActorCreated,
    ):
        return "actors.created"

    raise ValueError(
        "Unsupported event type "
        f"for outbox: "
        f"{event.__class__.__name__}"
    )