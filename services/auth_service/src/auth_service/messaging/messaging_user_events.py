import asyncio
import json
import aio_pika
import logging
from sqlalchemy import select

from auth_service.messaging.messaging_config import rabbitmq_settings
from auth_service.db.db_session import async_session
from auth_service.models.models_auth_user import AuthUser
from auth_service.models.models_processed_user_event import ProcessedUserEvent
from auth_service.repositories.repository_refresh_session import RefreshSessionRepository
from common.security.user_state import set_user_security_state
from common.messaging_contract import (
    AUTH_USER_SYNC_QUEUE, USER_EVENTS_EXCHANGE, USER_EVENTS_ROUTING_KEY,
)

logger = logging.getLogger(__name__)


async def consume_user_events_forever():
    while True:
        try:
            connection = await aio_pika.connect_robust(rabbitmq_settings.url)
            channel = await connection.channel()
            exchange = await channel.declare_exchange(USER_EVENTS_EXCHANGE, aio_pika.ExchangeType.FANOUT, durable=True)
            queue = await channel.declare_queue(AUTH_USER_SYNC_QUEUE, durable=True, exclusive=False, auto_delete=False)
            await queue.bind(exchange, routing_key=USER_EVENTS_ROUTING_KEY)
            logger.info("user-events consumer ready exchange=%s queue=%s routing_key=%r", USER_EVENTS_EXCHANGE, AUTH_USER_SYNC_QUEUE, USER_EVENTS_ROUTING_KEY)
            async with queue.iterator() as iterator:
                async for message in iterator:
                    async with message.process(requeue=True):
                        event = json.loads(message.body)
                        event_id = event.get("event_id")
                        if not event_id:
                            continue
                        async with async_session() as session:
                            try:
                                seen = await session.scalar(select(ProcessedUserEvent).where(ProcessedUserEvent.event_id == event_id))
                                if seen:
                                    continue
                                auth_id = event.get("auth_id")
                                user = await session.get(AuthUser, auth_id) if auth_id else None
                                if user is not None:
                                    event_type = event.get("event_type")
                                    if event_type == "user.role.changed" and event.get("role"):
                                        user.role = event["role"]
                                    if event_type == "user.activated":
                                        user.is_active = True
                                    if event_type in {"user.blocked", "user.deleted"}:
                                        user.is_active = False
                                    if event_type in {"user.role.changed", "user.blocked", "user.deleted", "user.activated"}:
                                        user.token_version += 1
                                        await RefreshSessionRepository(session).revoke_user(user.id, event_type)
                                    await set_user_security_state(
                                        auth_user_id=user.id,
                                        token_version=user.token_version,
                                        role=str(user.role.value if hasattr(user.role, "value") else user.role),
                                        status=("deleted" if event_type == "user.deleted" else "blocked" if event_type == "user.blocked" else "active"),
                                    )
                                session.add(ProcessedUserEvent(event_id=event_id))
                                await session.commit()
                            except Exception:
                                await session.rollback()
                                raise
            await connection.close()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("user-events consumer failed; retrying")
            await asyncio.sleep(5)
