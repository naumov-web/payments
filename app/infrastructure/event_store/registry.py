from app.domain.events.actor import ActorCreated
from app.domain.events.base import DomainEvent
from app.domain.events.transaction import TransactionCreated

EVENT_REGISTRY: dict[str, type[DomainEvent]] = {
    ActorCreated.__name__: ActorCreated,
    TransactionCreated.__name__: TransactionCreated,
}