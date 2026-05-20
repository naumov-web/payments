import asyncio

from app.application.actors.create_admin import (
    AdminAlreadyExistsError,
    CreateAdminUseCase,
)
from app.infrastructure.unit_of_work import UnitOfWork


async def create_admin():
    email = input("Email: ").strip()
    full_name = input("Full name: ").strip()

    use_case = CreateAdminUseCase(
        uow=UnitOfWork(),
    )

    try:
        await use_case.execute(
            email=email,
            full_name=full_name,
        )

    except AdminAlreadyExistsError as exc:
        print(str(exc))
        return

    print("Admin created successfully.")


if __name__ == "__main__":
    asyncio.run(create_admin())