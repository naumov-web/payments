from dataclasses import asdict, dataclass, field
from datetime import datetime, UTC
from uuid import UUID, uuid4


@dataclass(slots=True, kw_only=True)
class DomainEvent:
    aggregate_id: UUID

    event_id: UUID = field(default_factory=uuid4)

    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(UTC),
    )

    event_version: int = 1

    @property
    def event_type(self) -> str:
        return self.__class__.__name__

    def to_dict(self) -> dict:
        return asdict(self)