from uuid import UUID

from fastapi import APIRouter
from fastapi import HTTPException

from app.application.transactions.get_transaction_by_id import (
    GetTransactionByIdUseCase,
)
from app.application.transactions.get_transaction_by_id import (
    TransactionNotFoundError,
)
from app.infrastructure.unit_of_work import UnitOfWork
from app.interfaces.http.schemas.transaction_details import TransactionDetailsResponse


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
)


@router.get(
    "/{transaction_id}",
    response_model=TransactionDetailsResponse,
    summary="Get transaction by id",
)
async def get_transaction_by_id(
    transaction_id: UUID,
):
    use_case = (
        GetTransactionByIdUseCase(
            uow=UnitOfWork(),
        )
    )

    try:
        result = await (
            use_case.execute(
                transaction_id=transaction_id,
            )
        )

    except TransactionNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    return TransactionDetailsResponse(
        transaction_id=result[
            "transaction_id"
        ],
        transaction_type=result[
            "transaction_type"
        ],
        amount=result["amount"],
        sender_actor_id=result[
            "sender_actor_id"
        ],
        sender_name=result[
            "sender_name"
        ],
        receiver_actor_id=result[
            "receiver_actor_id"
        ],
        receiver_name=result[
            "receiver_name"
        ],
        reference_transaction_id=result[
            "reference_transaction_id"
        ],
        created_at=result[
            "created_at"
        ],
    )