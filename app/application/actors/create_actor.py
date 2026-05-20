from uuid import UUID

from app.domain.actors.aggregate import (
    ActorAggregate,
)
from app.domain.events.actor import ActorCreated
from app.infrastructure.projections.actor_projection import (
    ActorProjectionUpdater,
)
from app.infrastructure.unit_of_work import UnitOfWork


class ActorAlreadyExistsError(Exception):
    pass


class ActorIdAlreadyExistsError(Exception):
    pass


class CreateActorUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self._uow = uow

    async def execute(
        self,
        *,
        actor_id: UUID,
        email: str,
        full_name: str,
    ) -> None:
        async with self._uow as uow:
            existing_actor_by_id = (
                await uow.actors.get_by_id(
                    actor_id,
                )
            )

            if existing_actor_by_id:
                raise ActorIdAlreadyExistsError(
                    f"Actor with id {actor_id} already exists."
                )

            existing_actor_by_email = (
                await uow.actors.get_by_email(
                    email,
                )
            )

            if existing_actor_by_email:
                raise ActorAlreadyExistsError(
                    f"Actor with email {email} already exists."
                )

            aggregate = (
                ActorAggregate.create_employee(
                    aggregate_id=actor_id,
                    email=email,
                    full_name=full_name,
                )
            )

            events = (
                await uow.actor_aggregates.save(
                    aggregate,
                )
            )

            projection = ActorProjectionUpdater(
                repository=uow.actors,
            )

            for event in events:
                if isinstance(event, ActorCreated):
                    await projection.apply_actor_created(
                        event,
                    )