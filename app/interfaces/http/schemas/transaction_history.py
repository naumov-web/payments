from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TransactionHistoryItemResponse(
    BaseModel
):
    transaction_id: UUID

    transaction_type: str

    direction: str

    amount: int

    counterparty_actor_id: UUID

    counterparty_name: str

    reference_transaction_id: UUID | None

    created_at: datetime


class TransactionHistoryResponse(
    BaseModel
):
    total_count: int

    items: list[
        TransactionHistoryItemResponse
    ]