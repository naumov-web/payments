from app.domain.events.actor import ActorCreated
from app.domain.events.base import DomainEvent


class ActorAggregate:
    def __init__(self):
        self.id = None
        self.actor_type = None
        self.role = None
        self.email = None
        self.full_name = None
        self.version = 0
        self._uncommitted_events: list[DomainEvent] = []

    @classmethod
    def create_admin(
        cls,
        *,
        aggregate_id,
        email: str,
        full_name: str,
    ) -> "ActorAggregate":
        actor = cls()

        event = ActorCreated(
            aggregate_id=aggregate_id,
            actor_type="HUMAN",
            role="ADMIN",
            email=email,
            full_name=full_name,
        )

        actor._record_event(event)

        return actor

    @classmethod
    def create_employee(
        cls,
        *,
        aggregate_id,
        email: str,
        full_name: str,
    ) -> "ActorAggregate":
        actor = cls()

        event = ActorCreated(
            aggregate_id=aggregate_id,
            actor_type="HUMAN",
            role="EMPLOYEE",
            email=email,
            full_name=full_name,
        )

        actor._record_event(event)

        return actor

    @classmethod
    def create_service(
        cls,
        *,
        aggregate_id,
        name: str,
    ) -> "ActorAggregate":
        actor = cls()

        event = ActorCreated(
            aggregate_id=aggregate_id,
            actor_type="SERVICE",
            full_name=name,
            role=None,
            email=None,
        )

        actor._record_event(event)

        return actor

    def apply(self, event: DomainEvent) -> None:
        self._apply(event)
        self.version += 1

    def _record_event(self, event: DomainEvent) -> None:
        self._apply(event)
        self._uncommitted_events.append(event)

    def _apply(self, event: DomainEvent) -> None:
        handler_name = f"_apply_{event.event_type}"

        handler = getattr(self, handler_name, None)

        if handler is None:
            raise ValueError(f"No handler for {event.event_type}")

        handler(event)

    def _apply_ActorCreated(self, event: ActorCreated) -> None:
        self.id = event.aggregate_id
        self.actor_type = event.actor_type
        self.role = event.role
        self.email = event.email
        self.full_name = event.full_name

    def pull_events(self) -> list[DomainEvent]:
        events = self._uncommitted_events.copy()
        self._uncommitted_events.clear()

        return events