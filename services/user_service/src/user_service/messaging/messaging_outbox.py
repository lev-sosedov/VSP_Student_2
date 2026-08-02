"""Reliable transactional-outbox publisher for user security events."""
from __future__ import annotations

import asyncio
import json
import logging

import aio_pika

from common.messaging_contract import EventEnvelope, USER_EVENTS_EXCHANGE, USER_EVENTS_ROUTING_KEY
from common.messaging_reliability import RetryPolicy, event_message, publish_confirmed
from user_service.db.db_session import AsyncSessionLocal
from user_service.messaging.messaging_config import rabbitmq_settings
from user_service.repositories.repository_outbox import OutboxRepository

logger = logging.getLogger(__name__)
PUBLISH_RETRY_POLICY = RetryPolicy(max_attempts=5, base_delay_seconds=2, max_delay_seconds=60)


async def publish_outbox_forever() -> None:
    """Poll only unpublished rows; confirm before marking them published."""
    while True:
        connection = None
        try:
            connection = await aio_pika.connect_robust(
                rabbitmq_settings.url, heartbeat=rabbitmq_settings.heartbeat
            )
            channel = await connection.channel(publisher_confirms=True)
            await channel.set_qos(prefetch_count=rabbitmq_settings.prefetch_count)
            exchange = await channel.declare_exchange(
                USER_EVENTS_EXCHANGE, aio_pika.ExchangeType.FANOUT, durable=True
            )
            logger.info("user-events outbox publisher ready exchange=%s", USER_EVENTS_EXCHANGE)
            async with AsyncSessionLocal() as session:
                repo = OutboxRepository(session)
                for event in await repo.pending():
                    try:
                        payload = json.loads(event.payload)
                        envelope = EventEnvelope.create(
                            event_type=event.event_type,
                            producer="user-service",
                            event_version=event.event_version,
                            payload={
                                "user_id": event.user_id,
                                "auth_id": event.auth_id,
                                **payload,
                            },
                        )
                        # Preserve the durable event_id assigned in the outbox.
                        envelope.event_id = envelope.event_id.__class__(event.event_id)
                        await publish_confirmed(
                            exchange,
                            event_message(envelope),
                            routing_key=USER_EVENTS_ROUTING_KEY,
                        )
                        await repo.mark_published(event.event_id)
                    except Exception as exc:
                        # Keep the row for a later attempt; never lose an event.
                        await repo.mark_failed(
                            event.event_id,
                            type(exc).__name__,
                            retry_after_seconds=int(PUBLISH_RETRY_POLICY.delay(event.retry_count + 1)),
                        )
                await session.commit()
            await connection.close()
            await asyncio.sleep(2)
        except asyncio.CancelledError:
            if connection is not None and not connection.is_closed:
                await connection.close()
            raise
        except Exception:
            logger.exception("user-events outbox publisher failed; retrying with backoff")
            if connection is not None and not connection.is_closed:
                await connection.close()
            await asyncio.sleep(5)
