from uuid import uuid4

from app.domain.actors.aggregate import (
    ActorAggregate,
)
from app.domain.events.actor import ActorCreated
from app.infrastructure.projections.actor_projection import (
    ActorProjectionUpdater,
)
from app.infrastructure.unit_of_work import UnitOfWork


class AdminAlreadyExistsError(Exception):
    pass


class CreateAdminUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self._uow = uow

    async def execute(
        self,
        *,
        email: str,
        full_name: str,
    ) -> None:
        async with self._uow as uow:
            existing_actor = (
                await uow.actors.get_by_email(
                    email,
                )
            )

            if existing_actor:
                raise AdminAlreadyExistsError(
                    f"Actor with email {email} already exists."
                )

            actor_id = uuid4()

            aggregate = (
                ActorAggregate.create_admin(
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