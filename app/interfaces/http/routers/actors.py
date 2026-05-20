from fastapi import APIRouter, HTTPException, status

from app.application.actors.create_actor import (
    ActorAlreadyExistsError,
    ActorIdAlreadyExistsError,
    CreateActorUseCase,
)
from app.infrastructure.unit_of_work import UnitOfWork
from app.interfaces.http.schemas.actor import (
    CreateActorRequest,
    CreateActorResponse,
)

router = APIRouter(
    prefix="/actors",
    tags=["actors"],
)


@router.post(
    "",
    response_model=CreateActorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create employee actor",
    description=(
        "Creates a new employee actor "
        "from external identity provider."
    ),
    responses={
        201: {
            "description": "Actor successfully created.",
        },
        409: {
            "description": "Actor already exists.",
        },
    },
)
async def create_actor(
    request: CreateActorRequest,
) -> CreateActorResponse:
    use_case = CreateActorUseCase(
        uow=UnitOfWork(),
    )

    try:
        await use_case.execute(
            actor_id=request.actor_id,
            email=request.email,
            full_name=request.full_name,
        )

    except ActorAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    except ActorIdAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    return CreateActorResponse(
        actor_id=request.actor_id,
        status="created",
    )