import asyncio

from app.infrastructure.kafka.producer import (
    KafkaProducerAdapter,
)
from app.infrastructure.unit_of_work import (
    UnitOfWork,
)


class OutboxPublisherWorker:
    POLL_INTERVAL_SECONDS = 5

    def __init__(
        self,
        *,
        producer: KafkaProducerAdapter,
    ):
        self._producer = producer

    async def run(self) -> None:
        await self._producer.start()

        try:
            while True:
                await self._process_batch()

                await asyncio.sleep(
                    self.POLL_INTERVAL_SECONDS
                )

        finally:
            await self._producer.stop()

    async def _process_batch(
        self,
    ) -> None:
        async with UnitOfWork() as uow:
            messages = (
                await uow.outbox.get_pending(
                    limit=100,
                )
            )

            for message in messages:
                try:
                    await self._producer.publish(
                        topic=message.topic,
                        payload=message.payload,
                    )

                    await (
                        uow.outbox.mark_processed(
                            message.id,
                        )
                    )

                except Exception:
                    await (
                        uow.outbox.mark_failed(
                            message.id,
                        )
                    )