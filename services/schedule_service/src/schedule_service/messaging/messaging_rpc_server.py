import asyncio
import json
from enum import Enum as PythonEnum
from typing import Any

import aio_pika
from sqlalchemy import select

from schedule_service.db.db_session import AsyncSessionLocal
from schedule_service.messaging.messaging_config import (
    rabbitmq_settings
)
from schedule_service.models.model_lesson_schedule import (
    LessonSchedule
)


class ScheduleRpcServer:
    def __init__(self):
        self.connection: aio_pika.RobustConnection | None = None
        self.channel: aio_pika.RobustChannel | None = None
        self.queue: aio_pika.RobustQueue | None = None
        self.started: bool = False

    # =====================================================
    # START
    # =====================================================

    async def start(self) -> None:
        if self.started:
            return

        last_error: Exception | None = None

        for attempt in range(1, 11):
            try:
                self.connection = await aio_pika.connect_robust(
                    host=rabbitmq_settings.host,
                    port=rabbitmq_settings.port,
                    login=rabbitmq_settings.username,
                    password=rabbitmq_settings.password,
                    virtualhost=rabbitmq_settings.virtual_host,
                    heartbeat=rabbitmq_settings.heartbeat
                )

                self.channel = await self.connection.channel()

                await self.channel.set_qos(
                    prefetch_count=(
                        rabbitmq_settings.prefetch_count
                    )
                )

                self.queue = await self.channel.declare_queue(
                    rabbitmq_settings.schedule_rpc_queue,
                    durable=True
                )

                await self.queue.consume(
                    self.process_message
                )

                self.started = True

                print(
                    "[Schedule RPC] Server started",
                    flush=True
                )

                return

            except Exception as error:
                last_error = error

                print(
                    f"[Schedule RPC Server] Connection "
                    f"attempt {attempt}/10 failed: {error}",
                    flush=True
                )

                await asyncio.sleep(
                    rabbitmq_settings.reconnect_interval
                )

        raise ConnectionError(
            "Schedule RPC server could not connect "
            "to RabbitMQ"
        ) from last_error

    # =====================================================
    # PROCESS MESSAGE
    # =====================================================

    async def process_message(
        self,
        message: aio_pika.IncomingMessage
    ) -> None:
        async with message.process():
            response: dict[str, Any] = {
                "success": False,
                "error": "Unknown request"
            }

            try:
                request = json.loads(
                    message.body.decode()
                )

                method = request.get("method")
                payload = request.get(
                    "payload",
                    {}
                )

                if method == "lesson.get_by_id":
                    response = await self.get_lesson_by_id(
                        payload=payload
                    )

                else:
                    response = {
                        "success": False,
                        "error": (
                            f"Unknown RPC method: {method}"
                        )
                    }

            except Exception as error:
                response = {
                    "success": False,
                    "error": str(error)
                }

            if (
                message.reply_to
                and self.channel is not None
            ):
                await self.channel.default_exchange.publish(
                    aio_pika.Message(
                        body=json.dumps(
                            response
                        ).encode(),
                        correlation_id=(
                            message.correlation_id
                        ),
                        content_type="application/json"
                    ),
                    routing_key=message.reply_to
                )

    # =====================================================
    # SERIALIZE ENUM
    # =====================================================

    @staticmethod
    def serialize_value(
        value: Any
    ) -> Any:
        if isinstance(value, PythonEnum):
            return value.value

        return value

    # =====================================================
    # GET LESSON BY ID
    # =====================================================

    async def get_lesson_by_id(
        self,
        payload: dict[str, Any]
    ) -> dict[str, Any]:
        lesson_id = payload.get("lesson_id")

        if lesson_id is None:
            return {
                "success": False,
                "error": "lesson_id is required"
            }

        try:
            lesson_id = int(lesson_id)

        except (TypeError, ValueError):
            return {
                "success": False,
                "error": "lesson_id must be an integer"
            }

        async with AsyncSessionLocal() as session:
            query = select(LessonSchedule).where(
                LessonSchedule.id == lesson_id
            )

            result = await session.execute(query)

            lesson = result.scalar_one_or_none()

            if lesson is None:
                return {
                    "success": True,
                    "lesson": None
                }

            return {
                "success": True,
                "lesson": {
                    "id": lesson.id,
                    "group_id": lesson.group_id,
                    "teacher_id": lesson.teacher_id,
                    "room_id": lesson.room_id,
                    "template_id": lesson.template_id,
                    "status": self.serialize_value(
                        lesson.status
                    ),
                    "lesson_type": self.serialize_value(
                        lesson.lesson_type
                    ),
                    "is_extra": lesson.is_extra
                }
            }

    # =====================================================
    # STOP
    # =====================================================

    async def stop(self) -> None:
        if (
            self.channel is not None
            and not self.channel.is_closed
        ):
            await self.channel.close()

        if (
            self.connection is not None
            and not self.connection.is_closed
        ):
            await self.connection.close()

        self.queue = None
        self.channel = None
        self.connection = None
        self.started = False

        print(
            "[Schedule RPC] Server stopped",
            flush=True
        )


schedule_rpc_server = ScheduleRpcServer()