from aio_pika import IncomingMessage
from common.messaging_contract import EventContractError, parse_event_envelope
from common.messaging_reliability import dead_letter, retry_or_dead_letter, RetryPolicy

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
        self.retry_policy = RetryPolicy(max_attempts=3)

    # =====================================================
    # Обработка входящего сообщения
    # =====================================================

    async def process_message(
        self,
        message: IncomingMessage
    ):

        try:
            envelope = parse_event_envelope(message.body)
            await handlers.handle(event=envelope.event_type, payload=envelope.payload)
            await message.ack()
        except EventContractError:
            if self.channel is not None:
                await dead_letter(self.channel, message, queue_name=self.queue_name, reason="malformed_event")
        except Exception as exc:
            if self.channel is not None:
                await retry_or_dead_letter(self.channel, message, queue_name=self.queue_name, policy=self.retry_policy, reason=type(exc).__name__)


academic_consumer = AcademicConsumer()


# =====================================================
# Запуск consumer
# =====================================================

async def consume_academic_events():

    print("[Academic] RabbitMQ consumer started")

    await academic_consumer.start()
