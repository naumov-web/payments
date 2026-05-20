import asyncio

from app.application.actors.bootstrap_system_actors import (
    BootstrapSystemActorsUseCase,
)
from app.infrastructure.unit_of_work import UnitOfWork


async def bootstrap():
    use_case = (
        BootstrapSystemActorsUseCase(
            uow=UnitOfWork(),
        )
    )

    await use_case.execute()

    print("System actors bootstrapped.")


if __name__ == "__main__":
    asyncio.run(bootstrap())