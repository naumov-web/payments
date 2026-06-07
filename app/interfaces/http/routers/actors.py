from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from fastapi import Query

from app.application.actors.create_actor import (
    ActorAlreadyExistsError,
    ActorIdAlreadyExistsError,
    CreateActorUseCase,
)
from app.application.transactions.get_actor_transactions import GetActorTransactionsUseCase
from app.infrastructure.unit_of_work import UnitOfWork
from app.interfaces.http.schemas.actor import (
    CreateActorRequest,
    CreateActorResponse,
)
from app.interfaces.http.schemas.transaction_history import TransactionHistoryItemResponse
from app.interfaces.http.schemas.transaction_history import TransactionHistoryResponse
from app.application.actors.get_actor_by_id import (
    ActorNotFoundError,
    GetActorByIdUseCase,
)
from app.interfaces.http.schemas.actor_details import ActorDetailsResponse

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
async def create_actor(request: CreateActorRequest) -> CreateActorResponse:
    use_case = CreateActorUseCase(uow=UnitOfWork())

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

@router.get(
    "/{actor_id}/transactions",
    response_model=TransactionHistoryResponse,
    summary="Get actor transactions",
)
async def get_actor_transactions(
    actor_id: UUID,
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
):
    use_case = GetActorTransactionsUseCase(uow=UnitOfWork())

    result = await use_case.execute(
        actor_id=actor_id,
        limit=limit,
        offset=offset,
    )

    return TransactionHistoryResponse(
        total_count=result["total_count"],
        items=[
            TransactionHistoryItemResponse(
                transaction_id=item["transaction_id"],
                transaction_type=item["transaction_type"],
                direction=item["direction"],
                amount=item["amount"],
                counterparty_actor_id=item["counterparty_actor_id"],
                counterparty_name=item["counterparty_name"],
                reference_transaction_id=item["reference_transaction_id"],
                created_at=item["created_at"],
            )
            for item in result["items"]
        ],
    )

@router.get(
    "/{actor_id}",
    response_model=ActorDetailsResponse,
    summary="Get actor by id",
)
async def get_actor_by_id(actor_id: UUID):
    use_case = GetActorByIdUseCase(uow=UnitOfWork())

    try:
        result = await use_case.execute(actor_id=actor_id)
    except ActorNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    return ActorDetailsResponse(
        actor_id=result["actor_id"],
        name=result["name"],
        email=result["email"],
        role=result["role"],
        balance=result["balance"],
    )