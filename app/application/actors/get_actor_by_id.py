from uuid import UUID

from app.infrastructure.unit_of_work import (
    UnitOfWork,
)


class ActorNotFoundError(
    Exception
):
    pass


class GetActorByIdUseCase:
    def __init__(
        self,
        *,
        uow: UnitOfWork,
    ):
        self._uow = uow

    async def execute(
        self,
        *,
        actor_id: UUID,
    ) -> dict:
        async with self._uow as uow:
            result = await (
                uow.actor_details.get_by_actor_id(
                    actor_id,
                )
            )

            if result is None:
                raise ActorNotFoundError(
                    "Actor not found."
                )

            actor = result["actor"]

            return {
                "actor_id": actor.actor_id,
                "name": actor.full_name,
                "email": actor.email,
                "role": actor.role,
                "balance": result[
                    "balance"
                ],
            }