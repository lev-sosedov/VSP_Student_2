import json
import aio_pika


async def publish_user_created(data: dict):

    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@rabbitmq/"
    )

    channel = await connection.channel()


    exchange = await channel.declare_exchange(
        "user_events",
        aio_pika.ExchangeType.FANOUT
    )


    message = aio_pika.Message(
        body=json.dumps(data).encode()
    )


    await exchange.publish(
        message,
        routing_key=""
    )


    await connection.close()