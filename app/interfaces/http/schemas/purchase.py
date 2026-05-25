from uuid import UUID

from pydantic import BaseModel
from pydantic import Field


class CreatePurchaseRequest(
    BaseModel
):
    buyer_actor_id: UUID

    merchant_actor_id: UUID

    amount: int = Field(
        gt=0,
        description="Amount in cents",
    )


class CreatePurchaseResponse(
    BaseModel
):
    transaction_id: UUID