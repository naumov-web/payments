from uuid import UUID

from pydantic import BaseModel
from pydantic import Field

class CreateTransferRequest(BaseModel):
    sender_actor_id: UUID
    receiver_actor_id: UUID
    amount: int = Field(
        gt=0,
        description="Amount in cents",
    )

class CreateTransferResponse(BaseModel):
    transaction_id: UUID