from app.infrastructure.database.models.ledger_entry import (
    LedgerEntryModel,
)


class LedgerRepository:
    def __init__(self, session):
        self._session = session

    async def add_entry(
        self,
        *,
        transaction_id,
        actor_id,
        amount,
        transaction_type,
    ) -> None:
        entry = LedgerEntryModel(
            transaction_id=transaction_id,
            actor_id=actor_id,
            amount=amount,
            transaction_type=transaction_type,
        )

        self._session.add(entry)