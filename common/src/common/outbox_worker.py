"""Reusable at-least-once outbox worker for service-owned event tables."""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timedelta

import aio_pika
from sqlalchemy import select

from common.messaging_contract import EventEnvelope
from common.messaging_reliability import RetryPolicy, event_message, publish_confirmed

logger = logging.getLogger(__name__)


class OutboxWorker:
    def __init__(self, *, session_factory, model, exchange_name: str, producer: str, url: str, exchange_type=aio_pika.ExchangeType.TOPIC):
        self.session_factory = session_factory
        self.model = model
        self.exchange_name = exchange_name
        self.producer = producer
        self.url = url
        self.exchange_type = exchange_type
        self.retry_policy = RetryPolicy(max_attempts=5, base_delay_seconds=2, max_delay_seconds=60)
        self.started = False
        self._stop = asyncio.Event()

    async def run_forever(self):
        self.started = True
        self._stop.clear()
        try:
            while not self._stop.is_set():
                connection = None
                try:
                    connection = await aio_pika.connect_robust(self.url, heartbeat=60)
                    channel = await connection.channel(publisher_confirms=True)
                    exchange = await channel.declare_exchange(self.exchange_name, self.exchange_type, durable=True)
                    async with self.session_factory() as session:
                        rows = list((await session.execute(
                            select(self.model)
                            .where(self.model.published_at.is_(None), (self.model.next_attempt_at.is_(None) | (self.model.next_attempt_at <= datetime.utcnow())))
                            .order_by(self.model.created_at).limit(100).with_for_update(skip_locked=True)
                        )).scalars().all())
                        for row in rows:
                            try:
                                envelope = EventEnvelope(event_id=row.event_id, event_type=row.event_type, event_version=row.event_version, occurred_at=row.created_at, producer=row.producer, correlation_id=row.correlation_id, causation_id=row.causation_id, payload=json.loads(row.payload))
                                await publish_confirmed(exchange, event_message(envelope), routing_key=row.event_type, mandatory=True)
                                row.published_at = datetime.utcnow()
                                row.last_error_code = None
                            except Exception as exc:
                                row.retry_count += 1
                                row.last_error_code = type(exc).__name__[:64]
                            row.next_attempt_at = datetime.utcnow() + timedelta(seconds=int(self.retry_policy.delay(row.retry_count)))
                        await session.commit()
                    await connection.close()
                    await asyncio.wait_for(self._stop.wait(), timeout=2)
                except asyncio.TimeoutError:
                    continue
                except asyncio.CancelledError:
                    raise
                except Exception:
                    logger.exception("outbox worker temporarily unavailable")
                    if connection is not None and not connection.is_closed:
                        await connection.close()
                    try:
                        await asyncio.wait_for(self._stop.wait(), timeout=5)
                    except asyncio.TimeoutError:
                        pass
        finally:
            self.started = False

    async def stop(self):
        self._stop.set()
