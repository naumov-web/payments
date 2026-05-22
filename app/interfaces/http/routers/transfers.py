from uuid import UUID

from fastapi import APIRouter
from fastapi import Header
from fastapi import HTTPException
from fastapi import status

from app.application.transactions.transfer import (
    ActorNotFoundError,
)
from app.application.transactions.transfer import (
    IdempotencyConflictError,
)
from app.application.transactions.transfer import (
    InsufficientFundsError,
)
from app.application.transactions.transfer import (
    InvalidTransferError,
)
from app.application.transactions.transfer import (
    TransferUseCase,
)
from app.infrastructure.unit_of_work import (
    UnitOfWork,
)
from app.interfaces.http.schemas.transfer import (
    CreateTransferRequest,
)
from app.interfaces.http.schemas.transfer import (
    CreateTransferResponse,
)

router = APIRouter(
    prefix="/transfers",
    tags=["Transfers"],
)

@router.post(
    "",
    response_model=CreateTransferResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create transfer",
)
async def create_transfer(
    request: CreateTransferRequest,
    idempotency_key: str = Header(
        ...,
        alias="Idempotency-Key",
    ),
):
    use_case = TransferUseCase(
        uow=UnitOfWork(),
    )

    try:
        result = await use_case.execute(
            sender_actor_id=(
                request.sender_actor_id
            ),
            receiver_actor_id=(
                request.receiver_actor_id
            ),
            amount=request.amount,
            idempotency_key=idempotency_key,
        )

    except ActorNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except InsufficientFundsError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except InvalidTransferError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except IdempotencyConflictError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    return CreateTransferResponse(
        transaction_id=result[
            "transaction_id"
        ]
    )