from app.domain.events.actor import ActorCreated
from app.domain.events.base import DomainEvent
from app.domain.events.transaction import (
    MoneyGranted,
    MoneyTransferred,
    MoneyWithdrawn,
)

EVENT_REGISTRY: dict[str, type[DomainEvent]] = {
    ActorCreated.__name__: ActorCreated,
    MoneyGranted.__name__: MoneyGranted,
    MoneyTransferred.__name__: MoneyTransferred,
    MoneyWithdrawn.__name__: MoneyWithdrawn,
}