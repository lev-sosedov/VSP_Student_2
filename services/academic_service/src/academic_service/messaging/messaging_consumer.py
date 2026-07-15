import aio_pika
import asyncio

from academic_service.messaging.messaging_rabbit import RabbitConnection
from academic_service.messaging.messaging_config import rabbitmq_settings


class RabbitConsumer:

    def __init__(self, queue_name: str, routing_keys: list[str]):
        self.queue_name = queue_name
        self.routing_keys = routing_keys

        self._stopping = False

    # =====================================================
    # START CONSUMER (без while True)
    # =====================================================

    async def start(self):

        while not self._stopping:

            try:
                channel = await RabbitConnection.get_channel()

                exchange = await channel.declare_exchange(
                    rabbitmq_settings.exchange,
                    aio_pika.ExchangeType.TOPIC,
                    durable=rabbitmq_settings.durable
                )

                queue = await channel.declare_queue(
                    self.queue_name,
                    durable=True
                )

                for key in self.routing_keys:
                    await queue.bind(exchange, routing_key=key)

                await queue.consume(self.process_message)

                print("[RabbitMQ] Consumer started")

                return  # 👈 ВАЖНО: больше нет while True

            except Exception as e:

                print("[RabbitMQ] Connection error:", e)

                await asyncio.sleep(rabbitmq_settings.reconnect_interval)

    # =====================================================
    # STOP (graceful shutdown)
    # =====================================================

    async def stop(self):

        self._stopping = True

        await RabbitConnection.close()

    # =====================================================
    # OVERRIDE
    # =====================================================

    async def process_message(self, message: aio_pika.IncomingMessage):
        raise NotImplementedError