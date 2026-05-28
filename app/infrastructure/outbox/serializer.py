import json
from dataclasses import asdict

from app.domain.events.base import (
    DomainEvent,
)


def serialize_event(
    event: DomainEvent,
) -> dict:
    serialized = json.dumps(
        asdict(event),
        default=_json_default,
    )

    return json.loads(serialized)


def _json_default(value):
    if hasattr(value, "isoformat"):
        return value.isoformat()

    return str(value)