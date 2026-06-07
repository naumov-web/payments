from uuid import UUID

from fastapi import APIRouter
from fastapi import Header
from fastapi import HTTPException
from fastapi import status

from app.application.transactions.withdrawal import (
    ActorNotFoundError,
    IdempotencyConflictError,
    InsufficientFundsError,
    InvalidWithdrawalError,
    WithdrawalUseCase,
)
from app.infrastructure.unit_of_work import UnitOfWork
from app.interfaces.http.schemas.withdrawal import (
    CreateWithdrawalRequest,
    CreateWithdrawalResponse,
)

router = APIRouter(
    prefix="/withdrawals",
    tags=["Withdrawals"],
)

@router.post(
    "",
    response_model=CreateWithdrawalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create withdrawal",
)
async def create_withdrawal(
    request: CreateWithdrawalRequest,
    idempotency_key: str = Header(
        ...,
        alias="Idempotency-Key",
    ),
):
    use_case = WithdrawalUseCase(uow=UnitOfWork())

    try:
        result = await use_case.execute(
            actor_id=request.actor_id,
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

    except InvalidWithdrawalError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except IdempotencyConflictError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    return CreateWithdrawalResponse(
        transaction_id=UUID(result["transaction_id"])
    )