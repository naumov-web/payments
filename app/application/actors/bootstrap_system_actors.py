from app.config.system_actors import (
    SYSTEM_ACTORS,
)
from app.domain.actors.aggregate import (
    ActorAggregate,
)
from app.domain.events.actor import ActorCreated
from app.infrastructure.projections.actor_projection import (
    ActorProjectionUpdater,
)
from app.infrastructure.unit_of_work import UnitOfWork


class BootstrapSystemActorsUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self._uow = uow

    async def execute(self) -> None:
        async with self._uow as uow:
            projection = ActorProjectionUpdater(
                repository=uow.actors,
            )

            for config in SYSTEM_ACTORS:
                existing_actor = (
                    await uow.actors.get_by_id(
                        config["actor_id"],
                    )
                )

                if existing_actor:
                    continue

                aggregate = (
                    ActorAggregate.create_service(
                        aggregate_id=config["actor_id"],
                        name=config["name"],
                    )
                )

                events = (
                    await uow.actor_aggregates.save(
                        aggregate,
                    )
                )

                for event in events:
                    if isinstance(event, ActorCreated):
                        await projection.apply_actor_created(
                            event,
                        )