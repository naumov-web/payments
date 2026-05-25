from uuid import UUID

from fastapi import APIRouter
from fastapi import Header
from fastapi import HTTPException
from fastapi import status

from app.application.transactions.purchase import (
    ActorNotFoundError,
)
from app.application.transactions.purchase import (
    IdempotencyConflictError,
)
from app.application.transactions.purchase import (
    InsufficientFundsError,
)
from app.application.transactions.purchase import (
    InvalidPurchaseError,
)
from app.application.transactions.purchase import (
    PurchaseUseCase,
)
from app.infrastructure.unit_of_work import (
    UnitOfWork,
)
from app.interfaces.http.schemas.purchase import (
    CreatePurchaseRequest,
)
from app.interfaces.http.schemas.purchase import (
    CreatePurchaseResponse,
)


router = APIRouter(
    prefix="/purchases",
    tags=["Purchases"],
)


@router.post(
    "",
    response_model=CreatePurchaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create purchase",
)
async def create_purchase(
    request: CreatePurchaseRequest,
    idempotency_key: str = Header(
        ...,
        alias="Idempotency-Key",
    ),
):
    use_case = PurchaseUseCase(
        uow=UnitOfWork(),
    )

    try:
        result = await use_case.execute(
            buyer_actor_id=(
                request.buyer_actor_id
            ),
            merchant_actor_id=(
                request.merchant_actor_id
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

    except InvalidPurchaseError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except IdempotencyConflictError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    return CreatePurchaseResponse(
        transaction_id=UUID(
            result["transaction_id"]
        )
    )