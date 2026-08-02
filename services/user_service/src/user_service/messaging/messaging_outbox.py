import asyncio
import json
import aio_pika

from user_service.db.db_session import AsyncSessionLocal
from user_service.repositories.repository_outbox import OutboxRepository


async def publish_outbox_forever():
    while True:
        try:
            connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
            channel = await connection.channel()
            exchange = await channel.declare_exchange("user_events", aio_pika.ExchangeType.FANOUT, durable=True)
            async with AsyncSessionLocal() as session:
                repo = OutboxRepository(session)
                for event in await repo.pending():
                    body = {
                        "event_id": event.event_id, "event_type": event.event_type,
                        "event_version": event.event_version, "occurred_at": event.occurred_at.isoformat(),
                        "user_id": event.user_id, "auth_id": event.auth_id,
                        **json.loads(event.payload),
                    }
                    await exchange.publish(aio_pika.Message(body=json.dumps(body).encode()), routing_key="")
                    await repo.mark_published(event.event_id)
                await session.commit()
            await connection.close()
            await asyncio.sleep(2)
        except asyncio.CancelledError:
            raise
        except Exception:
            await asyncio.sleep(5)
