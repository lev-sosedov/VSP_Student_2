import json
from datetime import date, datetime, time
from enum import Enum
from typing import Any
from uuid import UUID

import aio_pika

from schedule_service.messaging.messaging_config import (
    rabbitmq_settings
)
from schedule_service.messaging.messaging_rabbit import (
    RabbitConnection
)


# =====================================================
# Преобразование специальных типов в JSON
# =====================================================

def json_default(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value

    if isinstance(value, (datetime, date, time)):
        return value.isoformat()

    if isinstance(value, UUID):
        return str(value)

    raise TypeError(
        f"Object of type {type(value).__name__} "
        f"is not JSON serializable"
    )


# =====================================================
# Publisher событий расписания
# =====================================================

class ScheduleEventPublisher:
    def __init__(self):
        self.channel: aio_pika.RobustChannel | None = None
        self.exchange: aio_pika.RobustExchange | None = None
        self.started: bool = False

    # =================================================
    # START
    # =================================================

    async def start(self) -> None:
        if self.started:
            return

        self.channel = await RabbitConnection.get_channel()

        self.exchange = await self.channel.declare_exchange(
            rabbitmq_settings.exchange,
            type=rabbitmq_settings.exchange_type,
            durable=rabbitmq_settings.durable
        )

        self.started = True

        print(
            "[Schedule Events] Publisher started",
            flush=True
        )

    # =================================================
    # PUBLISH
    # =================================================

    async def publish(
        self,
        routing_key: str,
        payload: dict[str, Any]
    ) -> None:
        if not self.started:
            await self.start()

        if self.exchange is None:
            raise RuntimeError(
                "RabbitMQ exchange is not initialized"
            )

        event = {
            "event": routing_key,
            "service": "schedule-service",
            "occurred_at": datetime.utcnow().isoformat(),
            "data": payload
        }

        message = aio_pika.Message(
            body=json.dumps(
                event,
                ensure_ascii=False,
                default=json_default
            ).encode("utf-8"),
            content_type="application/json",
            delivery_mode=(
                aio_pika.DeliveryMode.PERSISTENT
                if rabbitmq_settings.persistent_messages
                else aio_pika.DeliveryMode.NOT_PERSISTENT
            )
        )

        await self.exchange.publish(
            message=message,
            routing_key=routing_key,
            mandatory=rabbitmq_settings.mandatory
        )

    # =================================================
    # STOP
    # =================================================

    async def stop(self) -> None:
        self.exchange = None
        self.channel = None
        self.started = False

        print(
            "[Schedule Events] Publisher stopped",
            flush=True
        )


schedule_event_publisher = ScheduleEventPublisher()