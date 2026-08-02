import json

import aio_pika
import json
from uuid import uuid4
from common.messaging_contract import EventEnvelope
from common.messaging_reliability import event_message, publish_confirmed
from common.outbox_context import current_session
from academic_service.models.model_event_outbox import EventOutbox

from academic_service.messaging.messaging_rabbit import RabbitConnection
from academic_service.messaging.messaging_config import rabbitmq_settings


class RabbitPublisher:

    @staticmethod
    async def publish(
            routing_key: str,
            event: str,
            payload: dict
    ):
        session = current_session.get()
        if session is not None:
            session.add(EventOutbox(event_id=str(uuid4()), event_type=event, producer="academic-service", payload=json.dumps(payload, default=str)))
            return
        channel = await RabbitConnection.get_channel()

        exchange = await channel.declare_exchange(
            rabbitmq_settings.exchange,
            aio_pika.ExchangeType.TOPIC,
            durable=True
        )

        envelope = EventEnvelope.create(event_type=event, producer="academic-service", payload=payload)
        await publish_confirmed(exchange, event_message(envelope), routing_key=routing_key)


publisher = RabbitPublisher()
