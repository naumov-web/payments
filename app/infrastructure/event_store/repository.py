from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.events.base import DomainEvent
from app.infrastructure.database.models.event import EventModel
from app.infrastructure.event_store.mapper import (
    map_domain_event_to_model,
)


class ConcurrencyConflictError(Exception):
    pass


class EventStoreRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def append_events(
        self,
        *,
        aggregate_id: UUID,
        aggregate_type: str,
        events: Sequence[DomainEvent],
        expected_version: int,
    ) -> None:
        query = (
            select(EventModel.stream_version)
            .where(EventModel.aggregate_id == aggregate_id)
            .order_by(EventModel.stream_version.desc())
            .limit(1)
        )

        result = await self._session.execute(query)

        current_version = result.scalar_one_or_none() or 0

        if current_version != expected_version:
            raise ConcurrencyConflictError(
                f"Expected version {expected_version}, "
                f"but got {current_version}."
            )

        models: list[EventModel] = []

        stream_version = current_version

        for event in events:
            stream_version += 1

            model = map_domain_event_to_model(
                event,
                stream_version=stream_version,
                aggregate_type=aggregate_type,
            )

            models.append(model)

        self._session.add_all(models)

    async def load_events(
        self,
        aggregate_id: UUID,
    ) -> list[EventModel]:
        query = (
            select(EventModel)
            .where(EventModel.aggregate_id == aggregate_id)
            .order_by(EventModel.stream_version.asc())
        )

        result = await self._session.execute(query)

        return list(result.scalars().all())