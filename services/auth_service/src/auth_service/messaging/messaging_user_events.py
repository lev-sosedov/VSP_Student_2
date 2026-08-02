"""Idempotent user-security event consumer with bounded DLQ retry."""
from __future__ import annotations

import asyncio
import json
import logging
from uuid import UUID

import aio_pika
from sqlalchemy import select

from auth_service.db.db_session import async_session
from auth_service.messaging.messaging_config import rabbitmq_settings
from auth_service.models.models_auth_user import AuthUser
from auth_service.models.models_processed_user_event import ProcessedUserEvent
from auth_service.repositories.repository_refresh_session import RefreshSessionRepository
from common.messaging_contract import (
    AUTH_USER_SYNC_QUEUE,
    USER_EVENTS_EXCHANGE,
    USER_EVENTS_ROUTING_KEY,
    EventEnvelope,
    EventContractError,
    parse_event_envelope,
)
from common.messaging_reliability import RetryPolicy, declare_dlx, dead_letter, retry_or_dead_letter
from common.security.user_state import set_user_security_state

logger = logging.getLogger(__name__)
RETRY_POLICY = RetryPolicy(max_attempts=3, base_delay_seconds=1, max_delay_seconds=15)


def _legacy_envelope(event: dict) -> EventEnvelope:
    """Read pre-stage-11 rows during rollout without logging their payload."""
    event_type = event.get("event_type") or event.get("event")
    payload = event.get("payload") or event.get("data") or {}
    payload = {**payload}
    for key in ("user_id", "auth_id"):
        if key in event and key not in payload:
            payload[key] = event[key]
    raw_id = event.get("event_id")
    try:
        event_id = UUID(str(raw_id)) if raw_id else None
    except (TypeError, ValueError):
        event_id = None
    if event_id is None or not event_type:
        raise EventContractError("malformed event envelope")
    return EventEnvelope(
        event_id=event_id,
        event_type=str(event_type),
        event_version=int(event.get("event_version", 1)),
        occurred_at=event.get("occurred_at") or "1970-01-01T00:00:00+00:00",
        producer=str(event.get("producer", "legacy")),
        payload=payload,
    ).validate_supported_version()


async def _decode(body: bytes) -> EventEnvelope:
    try:
        return parse_event_envelope(body)
    except EventContractError:
        try:
            return _legacy_envelope(json.loads(body.decode("utf-8")))
        except Exception as exc:
            raise EventContractError("malformed event envelope") from exc


async def _apply(envelope: EventEnvelope, session) -> None:
    payload = envelope.payload
    auth_id = payload.get("auth_id")
    user = await session.get(AuthUser, int(auth_id)) if auth_id is not None else None
    if user is None:
        # Missing target is a permanent domain failure; commit the idempotency
        # marker so the broker cannot redeliver forever.
        session.add(ProcessedUserEvent(event_id=str(envelope.event_id)))
        return
    event_type = envelope.event_type
    if event_type == "user.role.changed" and payload.get("role"):
        user.role = payload["role"]
    if event_type == "user.activated":
        user.is_active = True
    elif event_type in {"user.blocked", "user.deleted"}:
        user.is_active = False
    if event_type in {"user.role.changed", "user.blocked", "user.deleted", "user.activated", "user.password.changed"}:
        user.token_version += 1
        await RefreshSessionRepository(session).revoke_user(user.id, event_type)
    status = "deleted" if event_type == "user.deleted" else "blocked" if event_type == "user.blocked" else "active"
    await set_user_security_state(
        auth_user_id=user.id,
        token_version=user.token_version,
        role=str(user.role.value if hasattr(user.role, "value") else user.role),
        status=status,
    )
    session.add(ProcessedUserEvent(event_id=str(envelope.event_id)))


async def _handle_message(message: aio_pika.IncomingMessage, channel, queue_name: str) -> None:
    try:
        envelope = await _decode(message.body)
    except EventContractError:
        await dead_letter(channel, message, queue_name=queue_name, reason="malformed_event")
        return
    try:
        async with async_session() as session:
            seen = await session.scalar(select(ProcessedUserEvent).where(ProcessedUserEvent.event_id == str(envelope.event_id)))
            if seen:
                await message.ack()
                return
            await _apply(envelope, session)
            await session.commit()
        # ACK is intentionally after the DB commit.
        await message.ack()
    except Exception as exc:
        await retry_or_dead_letter(
            channel,
            message,
            queue_name=queue_name,
            policy=RETRY_POLICY,
            reason=type(exc).__name__,
        )


async def consume_user_events_forever() -> None:
    while True:
        connection = None
        try:
            connection = await aio_pika.connect_robust(rabbitmq_settings.url, heartbeat=rabbitmq_settings.heartbeat)
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=rabbitmq_settings.prefetch_count)
            exchange = await channel.declare_exchange(USER_EVENTS_EXCHANGE, aio_pika.ExchangeType.FANOUT, durable=True)
            queue = await channel.declare_queue(AUTH_USER_SYNC_QUEUE, durable=True, exclusive=False, auto_delete=False)
            await queue.bind(exchange, routing_key=USER_EVENTS_ROUTING_KEY)
            await declare_dlx(channel, AUTH_USER_SYNC_QUEUE)
            logger.info("user-events consumer ready exchange=%s queue=%s", USER_EVENTS_EXCHANGE, AUTH_USER_SYNC_QUEUE)
            async with queue.iterator() as iterator:
                async for message in iterator:
                    await _handle_message(message, channel, AUTH_USER_SYNC_QUEUE)
        except asyncio.CancelledError:
            if connection is not None and not connection.is_closed:
                await connection.close()
            raise
        except Exception:
            logger.exception("user-events consumer failed; retrying with bounded backoff")
            if connection is not None and not connection.is_closed:
                await connection.close()
            await asyncio.sleep(5)
