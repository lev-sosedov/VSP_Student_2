import json
from datetime import date, datetime, time
from enum import Enum
from typing import Any
from uuid import UUID

import aio_pika
from uuid import uuid4
from common.messaging_contract import EventEnvelope
from common.messaging_reliability import event_message, publish_confirmed
from common.outbox_context import current_session
from communication_service.models.model_event_outbox import EventOutbox

from communication_service.messaging.messaging_config import (
    rabbitmq_settings
)
from communication_service.messaging.messaging_rabbit import (
    RabbitConnection
)


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


class CommunicationEventPublisher:
    def __init__(self):
        self.channel: aio_pika.RobustChannel | None = None
        self.exchange: aio_pika.RobustExchange | None = None
        self.started: bool = False

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
            "[Communication Events] Publisher started",
            flush=True
        )

    async def publish(
        self,
        routing_key: str,
        payload: dict[str, Any]
    ) -> None:
        session = current_session.get()
        if session is not None:
            session.add(EventOutbox(event_id=str(uuid4()), event_type=routing_key, producer="communication-service", payload=json.dumps(payload, default=json_default)))
            return
        if not self.started:
            await self.start()

        if self.exchange is None:
            raise RuntimeError(
                "RabbitMQ exchange is not initialized"
            )

        envelope = EventEnvelope.create(event_type=routing_key, producer="communication-service", payload=payload)
        await publish_confirmed(self.exchange, event_message(envelope, persistent=rabbitmq_settings.persistent_messages), routing_key=routing_key, mandatory=rabbitmq_settings.mandatory)

    async def stop(self) -> None:
        self.exchange = None
        self.channel = None
        self.started = False

        print(
            "[Communication Events] Publisher stopped",
            flush=True
        )


communication_event_publisher = CommunicationEventPublisher()
