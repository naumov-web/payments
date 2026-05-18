from dataclasses import dataclass
from uuid import UUID

from app.domain.events.base import DomainEvent


@dataclass(slots=True, kw_only=True)
class ActorCreated(DomainEvent):
    actor_type: str
    email: str | None = None
    full_name: str | None = None
    role: str | None = None