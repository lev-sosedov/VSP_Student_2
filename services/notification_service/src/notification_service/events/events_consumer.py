import asyncio
import json

import aio_pika

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
                        durable=True
                    )
                )

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
        async with message.process(
            requeue=False
        ):
            try:
                event = json.loads(
                    message.body.decode("utf-8")
                )

                event_type = (
                    event.get("event")
                    or message.routing_key
                )

                payload = event.get("data")

                if payload is None:
                    payload = event.get(
                        "payload",
                        {}
                    )

                if not isinstance(payload, dict):
                    raise ValueError(
                        "Event payload must be an object"
                    )

                async with AsyncSessionLocal() as session:
                    service = NotificationService(
                        session=session
                    )

                    if event_type.startswith(
                        "content."
                    ):
                        await (
                            content_event_handler
                            .handle(
                                event_type=event_type,
                                payload=payload,
                                service=service
                            )
                        )

                    elif event_type.startswith(
                        "schedule."
                    ):
                        await (
                            schedule_event_handler
                            .handle(
                                event_type=event_type,
                                payload=payload,
                                service=service
                            )
                        )

                    elif event_type.startswith(
                        "communication."
                    ):
                        await (
                            communication_event_handler
                            .handle(
                                event_type=event_type,
                                payload=payload,
                                service=service
                            )
                        )

                    elif event_type.startswith(
                        "news."
                    ):
                        await (
                            news_event_handler
                            .handle(
                                event_type=event_type,
                                payload=payload,
                                service=service
                            )
                        )

                    else:
                        print(
                            "[Notification Events] "
                            "Unsupported event: "
                            f"{event_type}",
                            flush=True
                        )

                    await session.commit()

                print(
                    "[Notification Events] "
                    f"Processed: {event_type}",
                    flush=True
                )

            except Exception as error:
                print(
                    "[Notification Events] "
                    f"Processing failed: {error}",
                    flush=True
                )

                raise

    # =================================================
    # STOP
    # =================================================

    async def stop(self) -> None:
        self._stopping = True
        self.started = False
        self.queue = None

        print(
            "[Notification Events] "
            "Consumer stopped",
            flush=True
        )


notification_event_consumer = (
    NotificationEventConsumer()
)