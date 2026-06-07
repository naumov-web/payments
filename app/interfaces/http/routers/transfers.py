from uuid import UUID

from fastapi import APIRouter
from fastapi import Header
from fastapi import HTTPException
from fastapi import status

from app.application.transactions.refund_transfer import (
    IdempotencyConflictError as RefundIdempotencyConflictError,
    InsufficientFundsError as RefundInsufficientFundsError,
    RefundAlreadyExistsError,
    RefundNotAllowedError,
    RefundTransferUseCase,
    RefundWindowExpiredError,
    TransactionNotFoundError,
)
from app.application.transactions.transfer import (
    ActorNotFoundError,
    IdempotencyConflictError,
    InsufficientFundsError,
    InvalidTransferError,
    TransferUseCase,
)
from app.infrastructure.unit_of_work import UnitOfWork
from app.interfaces.http.schemas.transfer import (
    CreateTransferRequest,
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
    use_case = TransferUseCase(uow=UnitOfWork())

    try:
        result = await use_case.execute(
            sender_actor_id=request.sender_actor_id,
            receiver_actor_id=request.receiver_actor_id,
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
        transaction_id=result["transaction_id"]
    )

@router.patch(
    "/{transaction_id}/refund",
    response_model=CreateTransferResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Refund transfer",
)
async def refund_transfer(
    transaction_id: UUID,
    idempotency_key: str = Header(
        ...,
        alias="Idempotency-Key",
    ),
):
    use_case = RefundTransferUseCase(uow=UnitOfWork())

    try:
        result = await use_case.execute(
            transaction_id=transaction_id,
            idempotency_key=idempotency_key,
        )

    except TransactionNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except RefundWindowExpiredError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except RefundAlreadyExistsError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except RefundNotAllowedError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except RefundInsufficientFundsError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except RefundIdempotencyConflictError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    return CreateTransferResponse(
        transaction_id=UUID(result["transaction_id"])
    )