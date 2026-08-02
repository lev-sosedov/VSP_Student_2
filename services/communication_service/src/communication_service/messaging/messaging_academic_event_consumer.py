import json

import aio_pika
from common.messaging_contract import EventContractError, parse_event_envelope
from common.messaging_reliability import RetryPolicy, declare_dlx, dead_letter, retry_or_dead_letter

from communication_service.core.core_config import settings
from communication_service.db.db_session import AsyncSessionLocal
from communication_service.messaging.messaging_config import (
    rabbitmq_settings
)
from communication_service.messaging.messaging_rabbit import (
    RabbitConnection
)
from communication_service.services.service_chat import ChatService
from communication_service.models.model_processed_event import ProcessedEvent
from sqlalchemy import select


class AcademicEventConsumer:
    def __init__(self):
        self.queue: aio_pika.RobustQueue | None = None
        self.consumer_tag: str | None = None
        self.started = False
        self.retry_policy = RetryPolicy(max_attempts=3)

    async def start(self) -> None:
        if self.started:
            return

        channel = await RabbitConnection.get_channel()

        exchange = await channel.declare_exchange(
            rabbitmq_settings.exchange,
            type=rabbitmq_settings.exchange_type,
            durable=rabbitmq_settings.durable
        )

        self.queue = await channel.declare_queue(
            rabbitmq_settings.academic_events_queue,
            durable=rabbitmq_settings.durable,
            exclusive=False,
            auto_delete=False,
        )
        await declare_dlx(channel, rabbitmq_settings.academic_events_queue)

        await self.queue.bind(
            exchange,
            routing_key=(
                rabbitmq_settings
                .academic_member_added_routing_key
            )
        )

        self.consumer_tag = await self.queue.consume(
            self._handle_message
        )

        self.started = True

        print(
            "[Communication Events] "
            "Academic member consumer started",
            flush=True
        )

    async def _handle_message(
        self,
        message: aio_pika.IncomingMessage
    ) -> None:
        try:
            envelope = parse_event_envelope(message.body)
            if envelope.event_type != rabbitmq_settings.academic_member_added_routing_key:
                await message.ack()
                return
            payload = envelope.payload

            group_id = int(
                payload.get("group_id", 0)
            )
            user_id = int(
                payload.get("user_id", 0)
            )
            role = str(
                payload.get("role", "")
            ).lower()

            if (
                group_id <= 0
                or user_id <= 0
                or role not in {"student", "teacher"}
            ):
                print(
                    "[Communication Events] "
                    "Incomplete academic member event skipped",
                    flush=True
                )
                return

            async with AsyncSessionLocal() as session:
                try:
                    seen = await session.scalar(select(ProcessedEvent).where(ProcessedEvent.event_id == str(envelope.event_id)))
                    if seen:
                        await message.ack()
                        return
                    service = ChatService(
                        session=session
                    )

                    await service.ensure_group_chat_member(
                        group_id=group_id,
                        user_id=user_id,
                        academic_role=role
                    )

                    if role == "student":
                        await service.ensure_admin_chat(
                            student_id=user_id,
                            admin_id=settings.ADMIN_USER_ID
                        )

                    session.add(ProcessedEvent(
                        event_id=str(envelope.event_id),
                        event_type=envelope.event_type,
                        producer=envelope.producer,
                    ))

                    await session.commit()

                except Exception:
                    await session.rollback()
                    raise
            await message.ack()
        except EventContractError:
            channel = await RabbitConnection.get_channel()
            await dead_letter(channel, message, queue_name=rabbitmq_settings.academic_events_queue, reason="malformed_event")
        except Exception as exc:
            channel = await RabbitConnection.get_channel()
            await retry_or_dead_letter(channel, message, queue_name=rabbitmq_settings.academic_events_queue, policy=self.retry_policy, reason=type(exc).__name__)

    async def stop(self) -> None:
        if (
            self.queue is not None
            and self.consumer_tag is not None
        ):
            await self.queue.cancel(
                self.consumer_tag
            )

        self.queue = None
        self.consumer_tag = None
        self.started = False

        print(
            "[Communication Events] "
            "Academic member consumer stopped",
            flush=True
        )


academic_event_consumer = AcademicEventConsumer()
