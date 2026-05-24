from uuid import UUID

from app.infrastructure.unit_of_work import (
    UnitOfWork,
)


class GetActorTransactionsUseCase:
    def __init__(
        self,
        *,
        uow: UnitOfWork,
    ):
        self._uow = uow

    async def execute(
        self,
        *,
        actor_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        async with self._uow as uow:
            result = await (
                uow.transaction_history.get_actor_transactions(
                    actor_id=actor_id,
                    limit=limit,
                    offset=offset,
                )
            )

            items: list[dict] = []

            for item in result["items"]:
                transaction = item[
                    "transaction"
                ]

                sender_name = item[
                    "sender_name"
                ]

                receiver_name = item[
                    "receiver_name"
                ]

                if (
                    transaction.sender_actor_id
                    == actor_id
                ):
                    direction = "OUTGOING"

                    counterparty_actor_id = (
                        transaction.receiver_actor_id
                    )

                    counterparty_name = (
                        receiver_name
                    )

                else:
                    direction = "INCOMING"

                    counterparty_actor_id = (
                        transaction.sender_actor_id
                    )

                    counterparty_name = (
                        sender_name
                    )

                items.append(
                    {
                        "transaction_id": (
                            transaction.transaction_id
                        ),
                        "transaction_type": (
                            transaction.transaction_type
                        ),
                        "direction": direction,
                        "amount": (
                            transaction.amount
                        ),
                        "counterparty_actor_id": (
                            counterparty_actor_id
                        ),
                        "counterparty_name": (
                            counterparty_name
                        ),
                        "reference_transaction_id": (
                            transaction.reference_transaction_id
                        ),
                        "created_at": (
                            transaction.created_at
                        ),
                    }
                )

            return {
                "total_count": result[
                    "total_count"
                ],
                "items": items,
            }