import asyncio
import json

import aio_pika
from common.messaging_contract import EventContractError, parse_event_envelope
from common.messaging_reliability import RetryPolicy, declare_dlx, dead_letter, retry_or_dead_letter
from notification_service.models.model_processed_event import ProcessedEvent
from sqlalchemy import select

from notification_service.db.db_session import (
    AsyncSessionLocal
)
from notification_service.events.events_communication_handler import (
    communication_event_handler
)
from notification_service.events.events_content_handler import (
    content_event_handler
)
from notification_service.events.events_news_handler import (
    news_event_handler
)
from notification_service.events.events_schedule_handler import (
    schedule_event_handler
)
from notification_service.messaging.messaging_config import (
    rabbitmq_settings
)
from notification_service.messaging.messaging_rabbit import (
    RabbitConnection
)
from notification_service.services.service_notification import (
    NotificationService
)


class NotificationEventConsumer:
    def __init__(self):
        self.queue: (
            aio_pika.RobustQueue | None
        ) = None

        self.started: bool = False
        self._stopping: bool = False
        self._channel = None
        self.retry_policy = RetryPolicy(max_attempts=3, base_delay_seconds=1, max_delay_seconds=15)

    # =================================================
    # START
    # =================================================

    async def start(self) -> None:
        if self.started:
            return

        self._stopping = False

        while not self._stopping:
            try:
                channel = (
                    await RabbitConnection.get_channel()
                )
                self._channel = channel

                exchange = (
                    await channel.declare_exchange(
                        rabbitmq_settings.exchange,
                        type=(
                            rabbitmq_settings.exchange_type
                        ),
                        durable=(
                            rabbitmq_settings.durable
                        )
                    )
                )

                self.queue = (
                    await channel.declare_queue(
                        rabbitmq_settings.queue,
                        durable=True,
                        exclusive=False,
                        auto_delete=False,
                    )
                )
                await declare_dlx(channel, rabbitmq_settings.queue)

                routing_keys = [
                    # =============================
                    # Content Service
                    # =============================

                    "content.homework.published",
                    "content.submission.needs_revision",
                    "content.submission.accepted",
                    "content.submission.rejected",

                    # =============================
                    # Schedule Service
                    # =============================

                    "schedule.lesson.created",
                    "schedule.lesson.rescheduled",
                    "schedule.lesson.cancelled",
                    "schedule.lesson.teacher_changed",
                    "schedule.lesson.room_changed",
                    "schedule.lesson.restored",

                    # =============================
                    # Communication Service
                    # =============================

                    "communication.message.created",

                    # =============================
                    # News Service
                    # =============================

                    "news.post.published",
                    "news.comment.created",
                    "news.comment.reply_created"
                ]

                for routing_key in routing_keys:
                    await self.queue.bind(
                        exchange,
                        routing_key=routing_key
                    )

                await self.queue.consume(
                    self.process_message
                )

                self.started = True

                print(
                    "[Notification Events] "
                    "Consumer started",
                    flush=True
                )

                return

            except Exception as error:
                print(
                    "[Notification Events] "
                    f"Connection error: {error}",
                    flush=True
                )

                await asyncio.sleep(
                    rabbitmq_settings
                    .reconnect_interval
                )

    # =================================================
    # PROCESS MESSAGE
    # =================================================

    async def process_message(
        self,
        message: aio_pika.IncomingMessage
    ) -> None:
        try:
            try:
                envelope = parse_event_envelope(message.body)
                event_type = envelope.event_type
                payload = envelope.payload
                event_id = str(envelope.event_id)
                producer = envelope.producer
            except EventContractError:
                # Compatibility for messages emitted immediately before the
                # envelope rollout; malformed messages are DLQ'd below.
                event = json.loads(message.body.decode("utf-8"))
                event_type = event.get("event") or event.get("event_type") or message.routing_key
                payload = event.get("data") or event.get("payload") or {}
                event_id = str(event.get("event_id", ""))
                producer = str(event.get("service", "legacy"))
                if not event_id or not isinstance(payload, dict):
                    raise EventContractError("malformed event envelope")

            async with AsyncSessionLocal() as session:
                seen = await session.scalar(select(ProcessedEvent).where(ProcessedEvent.event_id == event_id))
                if seen:
                    await message.ack()
                    return

                service = NotificationService(session=session)

                if event_type.startswith("content."):
                    await content_event_handler.handle(event_type=event_type, payload=payload, service=service)
                elif event_type.startswith("schedule."):
                    await schedule_event_handler.handle(event_type=event_type, payload=payload, service=service)
                elif event_type.startswith("communication."):
                    await communication_event_handler.handle(event_type=event_type, payload=payload, service=service)
                elif event_type.startswith("news."):
                    await news_event_handler.handle(event_type=event_type, payload=payload, service=service)

                session.add(ProcessedEvent(event_id=event_id, event_type=event_type, producer=producer))
                await session.commit()

                print(
                    "[Notification Events] "
                    f"Processed: {event_type}",
                    flush=True
                )

            await message.ack()

        except EventContractError:
            if self._channel is not None:
                await dead_letter(self._channel, message, queue_name=rabbitmq_settings.queue, reason="malformed_event")
        except Exception as error:
            print("[Notification Events] Processing failed", flush=True)
            if self._channel is not None:
                await retry_or_dead_letter(self._channel, message, queue_name=rabbitmq_settings.queue, policy=self.retry_policy, reason=type(error).__name__)

    # =================================================
    # STOP
    # =================================================

    async def stop(self) -> None:
        self._stopping = True
        self.started = False
        self.queue = None
        self._channel = None

        print(
            "[Notification Events] "
            "Consumer stopped",
            flush=True
        )


notification_event_consumer = (
    NotificationEventConsumer()
)
