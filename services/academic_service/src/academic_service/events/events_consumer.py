import json

from aio_pika import IncomingMessage

from academic_service.messaging.messaging_consumer import RabbitConsumer
from academic_service.messaging.messaging_config import (
    ACADEMIC_QUEUE,
    ACADEMIC_ROUTING_KEYS,
)

from academic_service.events.events_handlers import handlers


class AcademicConsumer(RabbitConsumer):

    def __init__(self):
        super().__init__(
            queue_name=ACADEMIC_QUEUE,
            routing_keys=ACADEMIC_ROUTING_KEYS
        )

    # =====================================================
    # Обработка входящего сообщения
    # =====================================================

    async def process_message(
        self,
        message: IncomingMessage
    ):

        async with message.process():

            try:

                data = json.loads(message.body.decode())

                event = data.get("event")
                payload = data.get("payload", {})

                print(f"[Academic] Event: {event}")

                await handlers.handle(
                    event=event,
                    payload=payload
                )

            except Exception as e:

                print(
                    "[Academic] Error processing message:",
                    e
                )


academic_consumer = AcademicConsumer()


# =====================================================
# Запуск consumer
# =====================================================

async def consume_academic_events():

    print("[Academic] RabbitMQ consumer started")

    await academic_consumer.start()