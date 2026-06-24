import json
import aio_pika

from user_service.schemas.events import UserCreatedEvent

async def consume_user_events(service):
    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
    channel = await connection.channel()
    exchange = await channel.declare_exchange("user_events", aio_pika.ExchangeType.FANOUT)
    queue = await channel.declare_queue("user_created")

    await queue.bind(exchange)

    async with queue.iterator() as q:
        async for message in q:
            async with message.process():
                data = json.loads(message.body.decode())
                event = UserCreatedEvent.model_validate(data)

                print("EVENT RECEIVED:", data)

                await service.create_user_from_event(event)