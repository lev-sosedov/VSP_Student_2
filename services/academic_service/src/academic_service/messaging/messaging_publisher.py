import json

import aio_pika

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

        message = aio_pika.Message(
            body=json.dumps({
                "event": event,
                "payload": payload
            }).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type="application/json"
        )

        await exchange.publish(
            message,
            routing_key=routing_key
        )


publisher = RabbitPublisher()