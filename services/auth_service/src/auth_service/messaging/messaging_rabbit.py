import json
import aio_pika
from auth_service.messaging.messaging_config import rabbitmq_settings


async def publish_user_created(data: dict):
    connection = await aio_pika.connect_robust(rabbitmq_settings.url)
    channel = await connection.channel()
    exchange = await channel.declare_exchange("user_events",aio_pika.ExchangeType.FANOUT)
    message = aio_pika.Message(body=json.dumps(data).encode())
    await exchange.publish(message,routing_key="")
    await connection.close()
