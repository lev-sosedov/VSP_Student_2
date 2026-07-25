import json

import aio_pika

from communication_service.core.core_config import settings
from communication_service.db.db_session import AsyncSessionLocal
from communication_service.messaging.messaging_config import (
    rabbitmq_settings
)
from communication_service.messaging.messaging_rabbit import (
    RabbitConnection
)
from communication_service.services.service_chat import ChatService


class AcademicEventConsumer:
    def __init__(self):
        self.queue: aio_pika.RobustQueue | None = None
        self.consumer_tag: str | None = None
        self.started = False

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
            durable=rabbitmq_settings.durable
        )

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
        async with message.process(requeue=True):
            try:
                event = json.loads(
                    message.body.decode("utf-8")
                )
            except (UnicodeDecodeError, json.JSONDecodeError):
                print(
                    "[Communication Events] "
                    "Invalid academic event skipped",
                    flush=True
                )
                return

            if (
                event.get("event")
                != rabbitmq_settings
                .academic_member_added_routing_key
            ):
                return

            payload = (
                event.get("payload")
                or event.get("data")
                or {}
            )

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

                    await session.commit()

                except Exception:
                    await session.rollback()
                    raise

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
