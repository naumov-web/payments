from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from app.domain.events.base import DomainEvent
from app.domain.transactions.entities import (
    LedgerEntry,
)

@dataclass(slots=True, kw_only=True)
class MoneyGranted(DomainEvent):
    recipient_actor_id: UUID
    amount: Decimal
    currency: str


@dataclass(slots=True, kw_only=True)
class MoneyTransferred(DomainEvent):
    sender_actor_id: UUID
    receiver_actor_id: UUID
    amount: Decimal
    currency: str
    message: str | None = None


@dataclass(slots=True, kw_only=True)
class MoneyWithdrawn(DomainEvent):
    actor_id: UUID
    usd_amount: Decimal
    target_currency: str
    fx_rate: Decimal
    converted_amount: Decimal

@dataclass(slots=True, kw_only=True)
class TransactionCreated(DomainEvent):
    transaction_type: str
    entries: list[LedgerEntry]