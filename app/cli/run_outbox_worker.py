import asyncio
import os

from app.infrastructure.kafka.producer import (
    KafkaProducerAdapter,
)
from app.workers.outbox_publisher import (
    OutboxPublisherWorker,
)


async def main():
    bootstrap_servers = os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS",
        "kafka:9092",
    )

    producer = KafkaProducerAdapter(
        bootstrap_servers=(
            bootstrap_servers
        ),
    )

    worker = OutboxPublisherWorker(
        producer=producer,
    )

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())