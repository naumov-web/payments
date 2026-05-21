from uuid import UUID

from app.domain.events.base import DomainEvent
from app.domain.events.transaction import (
    TransactionCreated,
)
from app.domain.transactions.entities import (
    LedgerEntry,
)
from app.infrastructure.database.models.event import (
    EventModel,
)
from app.infrastructure.event_store.registry import (
    EVENT_REGISTRY,
)
from app.infrastructure.event_store.serializer import (
    serialize_value,
)


def map_domain_event_to_model(
    event: DomainEvent,
    *,
    stream_version: int,
    aggregate_type: str,
) -> EventModel:
    payload = serialize_value(event.to_dict())

    payload.pop("event_id", None)
    payload.pop("occurred_at", None)
    payload.pop("event_version", None)
    payload.pop("aggregate_id", None)

    return EventModel(
        event_id=event.event_id,
        aggregate_id=event.aggregate_id,
        aggregate_type=aggregate_type,
        stream_version=stream_version,
        event_type=event.event_type,
        event_version=event.event_version,
        payload=payload,
        event_metadata={},
        occurred_at=event.occurred_at,
    )


def map_model_to_domain_event(
    model: EventModel,
) -> DomainEvent:
    event_class = EVENT_REGISTRY.get(
        model.event_type,
    )

    if event_class is None:
        raise ValueError(
            f"Unknown event type: {model.event_type}"
        )

    payload = dict(model.payload)

    if event_class is TransactionCreated:
        payload["entries"] = [
            LedgerEntry(
                actor_id=UUID(entry["actor_id"]),
                amount=entry["amount"],
            )
            for entry in payload["entries"]
        ]

    return event_class(
        aggregate_id=model.aggregate_id,
        event_id=model.event_id,
        occurred_at=model.occurred_at,
        event_version=model.event_version,
        **payload,
    )