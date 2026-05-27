from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TransactionDetailsResponse(
    BaseModel
):
    transaction_id: UUID
    transaction_type: str
    amount: int

    sender_actor_id: UUID

    sender_name: str

    receiver_actor_id: UUID

    receiver_name: str

    reference_transaction_id: UUID | None

    created_at: datetime