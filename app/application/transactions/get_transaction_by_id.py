from uuid import UUID
from app.infrastructure.unit_of_work import UnitOfWork

class TransactionNotFoundError(Exception):
    pass

class GetTransactionByIdUseCase:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    async def execute(self, *, transaction_id: UUID) -> dict:
        async with self._uow as uow:
            result = await uow.transaction_details.get_by_transaction_id(transaction_id)

            if result is None:
                raise TransactionNotFoundError("Transaction not found.")

            transaction = result["transaction"]

            return {
                "transaction_id": transaction.transaction_id,
                "transaction_type": transaction.transaction_type,
                "amount": transaction.amount,
                "sender_actor_id": transaction.sender_actor_id,
                "sender_name": result["sender_name"],
                "receiver_actor_id": transaction.receiver_actor_id,
                "receiver_name": result["receiver_name"],
                "reference_transaction_id": transaction.reference_transaction_id,
                "created_at": transaction.created_at,
            }