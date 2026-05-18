import asyncio
from uuid import uuid4

from app.domain.events.actor import ActorCreated
from app.infrastructure.projections.actor_projection import (
    ActorProjectionUpdater,
)
from app.infrastructure.unit_of_work import UnitOfWork


async def create_admin():
    email = input("Email: ").strip()
    full_name = input("Full name: ").strip()

    actor_id = uuid4()

    event = ActorCreated(
        aggregate_id=actor_id,
        actor_type="HUMAN",
        role="ADMIN",
        email=email,
        full_name=full_name,
    )

    async with UnitOfWork() as uow:
        await uow.event_store_repository.append_events(
            aggregate_id=actor_id,
            aggregate_type="ACTOR",
            events=[event],
            expected_version=0,
        )

        projection = ActorProjectionUpdater(
            repository=uow.actors,
        )

        await projection.apply_actor_created(event)

    print("Admin created successfully.")


if __name__ == "__main__":
    asyncio.run(create_admin())