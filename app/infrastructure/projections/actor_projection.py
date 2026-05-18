from app.domain.events.actor import ActorCreated
from app.infrastructure.database.models.actor import ActorModel
from app.infrastructure.repositories.actor_repository import (
    ActorRepository,
)


class ActorProjectionUpdater:
    def __init__(
        self,
        repository: ActorRepository,
    ):
        self._repository = repository

    async def apply_actor_created(
        self,
        event: ActorCreated,
    ) -> None:
        actor = ActorModel(
            actor_id=event.aggregate_id,
            actor_type=event.actor_type,
            role=event.role,
            email=event.email,
            full_name=event.full_name,
        )

        await self._repository.add(actor)