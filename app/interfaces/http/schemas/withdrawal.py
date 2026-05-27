from uuid import UUID

from pydantic import BaseModel
from pydantic import Field


class CreateWithdrawalRequest(
    BaseModel
):
    actor_id: UUID

    amount: int = Field(
        gt=0,
        description="Amount in cents",
    )


class CreateWithdrawalResponse(
    BaseModel
):
    transaction_id: UUID