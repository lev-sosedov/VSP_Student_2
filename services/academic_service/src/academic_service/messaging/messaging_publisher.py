import json

import aio_pika
from common.messaging_contract import EventEnvelope
from common.messaging_reliability import event_message, publish_confirmed

from academic_service.messaging.messaging_rabbit import RabbitConnection
from academic_service.messaging.messaging_config import rabbitmq_settings


class RabbitPublisher:

    @staticmethod
    async def publish(
            routing_key: str,
            event: str,
            payload: dict
    ):
        channel = await RabbitConnection.get_channel()

        exchange = await channel.declare_exchange(
            rabbitmq_settings.exchange,
            aio_pika.ExchangeType.TOPIC,
            durable=True
        )

        envelope = EventEnvelope.create(event_type=event, producer="academic-service", payload=payload)
        await publish_confirmed(exchange, event_message(envelope), routing_key=routing_key)


publisher = RabbitPublisher()
