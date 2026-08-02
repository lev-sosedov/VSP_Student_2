"""Small, dependency-light RabbitMQ reliability primitives.

Services keep their existing exchanges and queues.  This module only adds
versioned DLX topology and common delivery/publish semantics, so introducing
it cannot change an existing queue's arguments.
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

import aio_pika

from common.messaging_contract import EventEnvelope

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 30.0

    def delay(self, attempt: int) -> float:
        return min(self.max_delay_seconds, self.base_delay_seconds * (2 ** max(0, attempt - 1)))


def dlx_names(queue_name: str) -> tuple[str, str]:
    """Return stable, versioned DLX/DLQ names without altering the source queue."""
    safe = queue_name.replace("/", "_")
    return f"{safe}.v1.dlx", f"{safe}.v1.dlq"


async def declare_dlx(channel: aio_pika.abc.AbstractChannel, queue_name: str):
    exchange_name, dead_queue_name = dlx_names(queue_name)
    exchange = await channel.declare_exchange(
        exchange_name, aio_pika.ExchangeType.DIRECT, durable=True
    )
    queue = await channel.declare_queue(dead_queue_name, durable=True, exclusive=False, auto_delete=False)
    await queue.bind(exchange, routing_key=queue_name)
    return exchange, queue


async def publish_confirmed(
    exchange: aio_pika.abc.AbstractExchange,
    message: aio_pika.Message,
    *,
    routing_key: str,
    mandatory: bool = True,
) -> None:
    """Publish persistent data and wait for broker confirms."""
    await exchange.publish(message, routing_key=routing_key, mandatory=mandatory)


async def dead_letter(
    channel: aio_pika.abc.AbstractChannel,
    message: aio_pika.IncomingMessage,
    *,
    queue_name: str,
    reason: str,
) -> None:
    """Copy a failed delivery to the versioned DLQ, then ACK the source."""
    exchange_name, _ = dlx_names(queue_name)
    exchange = await channel.declare_exchange(exchange_name, aio_pika.ExchangeType.DIRECT, durable=True)
    headers = dict(message.headers or {})
    headers["x-failure-reason"] = reason[:160]
    dead = aio_pika.Message(
        body=message.body,
        headers=headers,
        content_type=message.content_type or "application/json",
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        correlation_id=message.correlation_id,
    )
    await exchange.publish(dead, routing_key=queue_name, mandatory=True)
    await message.ack()


def event_message(envelope: EventEnvelope, *, persistent: bool = True) -> aio_pika.Message:
    return aio_pika.Message(
        body=envelope.model_dump_json().encode("utf-8"),
        content_type="application/json",
        delivery_mode=(aio_pika.DeliveryMode.PERSISTENT if persistent else aio_pika.DeliveryMode.NOT_PERSISTENT),
        correlation_id=str(envelope.correlation_id) if envelope.correlation_id else None,
    )


async def retry_or_dead_letter(
    channel: aio_pika.abc.AbstractChannel,
    message: aio_pika.IncomingMessage,
    *,
    queue_name: str,
    policy: RetryPolicy,
    reason: str,
) -> None:
    """Bound retries using a fresh delayed delivery; never a tight requeue loop."""
    headers = dict(message.headers or {})
    try:
        attempt = int(headers.get("x-retry-count", 0)) + 1
    except (TypeError, ValueError):
        attempt = 1
    if attempt > policy.max_attempts:
        await dead_letter(channel, message, queue_name=queue_name, reason=reason)
        return
    headers["x-retry-count"] = attempt
    await asyncio.sleep(policy.delay(attempt))
    # A bounded retry is published back to the original queue through its
    # default exchange; the current delivery is acknowledged only afterwards.
    retry = aio_pika.Message(
        body=message.body,
        headers=headers,
        content_type=message.content_type or "application/json",
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        correlation_id=message.correlation_id,
    )
    await channel.default_exchange.publish(retry, routing_key=queue_name, mandatory=True)
    await message.ack()


class ComponentReadiness:
    """In-process readiness state used by `/ready` endpoints."""

    def __init__(self) -> None:
        self._state: dict[str, bool] = {}

    def mark(self, component: str, ready: bool) -> None:
        self._state[component] = bool(ready)

    def snapshot(self) -> dict[str, bool]:
        return dict(self._state)

    @property
    def ready(self) -> bool:
        return bool(self._state) and all(self._state.values())


def json_safe_log_fields(**fields: Any) -> dict[str, Any]:
    """Allow operational identifiers, never credential/token payloads."""
    blocked = ("password", "token", "jwt", "secret", "phone", "email", "payload")
    return {k: v for k, v in fields.items() if not any(word in k.lower() for word in blocked)}
