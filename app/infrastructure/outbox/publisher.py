from app.domain.events.base import (
    DomainEvent,
)
from app.infrastructure.outbox.topics import build_outbox_topic
from app.infrastructure.repositories.outbox_repository import OutboxRepository
from app.infrastructure.outbox.serializer import serialize_event

class OutboxEventPublisher:
    def __init__(self, repository: OutboxRepository):
        self._repository = repository

    async def publish(
        self,
        events: list[DomainEvent],
    ) -> None:
        for event in events:
            topic = build_outbox_topic(event)
            payload = serialize_event(event)

            await self._repository.add(
                topic=topic,
                payload=payload,
            )