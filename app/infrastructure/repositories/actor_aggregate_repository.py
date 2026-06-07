from uuid import UUID

from app.domain.actors.aggregate import ActorAggregate
from app.domain.events.base import DomainEvent
from app.infrastructure.event_store.mapper import map_model_to_domain_event
from app.infrastructure.event_store.store import EventStore

class ActorAggregateRepository:
    AGGREGATE_TYPE = "ACTOR"

    def __init__(self, event_store: EventStore):
        self._event_store = event_store

    async def load(self, aggregate_id: UUID) -> ActorAggregate:
        aggregate = ActorAggregate()

        models = await self._event_store.load_events(aggregate_id)

        for model in models:
            event = map_model_to_domain_event(model)

            aggregate.apply(event)

        return aggregate

    async def save(self, aggregate: ActorAggregate) -> list[DomainEvent]:
        events = aggregate.pull_events()

        if not events:
            return []

        expected_version = aggregate.version

        await self._event_store.append_events(
            aggregate_id=aggregate.id,
            aggregate_type=self.AGGREGATE_TYPE,
            events=events,
            expected_version=expected_version,
        )

        aggregate.version += len(events)

        return events