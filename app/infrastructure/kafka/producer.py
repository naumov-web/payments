import json

from aiokafka import AIOKafkaProducer

class KafkaProducerAdapter:
    def __init__(
        self,
        *,
        bootstrap_servers: str,
    ):
        self._producer = (
            AIOKafkaProducer(
                bootstrap_servers=(
                    bootstrap_servers
                ),
                value_serializer=(
                    lambda value: json.dumps(
                        value,
                    ).encode("utf-8")
                ),
            )
        )

    async def start(self) -> None:
        await self._producer.start()

    async def stop(self) -> None:
        await self._producer.stop()

    async def publish(
        self,
        *,
        topic: str,
        payload: dict,
    ) -> None:
        await self._producer.send_and_wait(
            topic,
            payload,
        )