from dataclasses import dataclass
from uuid import UUID

@dataclass(slots=True, frozen=True)
class LedgerEntry:
    actor_id: UUID
    amount: int