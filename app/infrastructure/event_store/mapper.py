from app.domain.events.base import DomainEvent
from app.infrastructure.database.models.event import EventModel
from app.infrastructure.event_store.serializer import serialize_value


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