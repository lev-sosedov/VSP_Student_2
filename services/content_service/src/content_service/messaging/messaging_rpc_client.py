import asyncio
import json
import uuid
from typing import Any

import aio_pika

from content_service.messaging.messaging_config import (
    rabbitmq_settings
)
from content_service.messaging.messaging_rabbit import (
    RabbitConnection
)


class RabbitRpcClient:
    def __init__(self):
        self.channel: aio_pika.RobustChannel | None = None
        self.callback_queue: aio_pika.RobustQueue | None = None
        self.futures: dict[str, asyncio.Future] = {}
        self.started: bool = False

    async def start(self) -> None:
        if self.started:
            return

        last_error: Exception | None = None

        for attempt in range(1, 11):
            try:
                self.channel = await RabbitConnection.get_channel()

                self.callback_queue = (
                    await self.channel.declare_queue(
                        exclusive=True,
                        auto_delete=True
                    )
                )

                await self.callback_queue.consume(
                    self.on_response,
                    no_ack=True
                )

                self.started = True

                print(
                    "[Content RPC] Client started",
                    flush=True
                )

                return

            except Exception as error:
                last_error = error

                print(
                    f"[Content RPC] Connection attempt "
                    f"{attempt}/10 failed: {error}",
                    flush=True
                )

                await asyncio.sleep(
                    rabbitmq_settings.reconnect_interval
                )

        raise ConnectionError(
            "Content RPC client could not connect "
            "to RabbitMQ"
        ) from last_error

    async def on_response(
        self,
        message: aio_pika.IncomingMessage
    ) -> None:
        correlation_id = message.correlation_id

        if not correlation_id:
            return

        future = self.futures.pop(
            correlation_id,
            None
        )

        if future is None or future.done():
            return

        try:
            response = json.loads(
                message.body.decode()
            )

            future.set_result(response)

        except Exception as error:
            future.set_exception(error)

    async def call(
        self,
        queue_name: str,
        method: str,
        payload: dict[str, Any],
        timeout: float = 5.0
    ) -> dict[str, Any]:
        if not self.started:
            await self.start()

        if self.channel is None:
            raise RuntimeError(
                "RabbitMQ channel is not initialized"
            )

        if self.callback_queue is None:
            raise RuntimeError(
                "RabbitMQ callback queue is not initialized"
            )

        correlation_id = str(uuid.uuid4())

        loop = asyncio.get_running_loop()
        future = loop.create_future()

        self.futures[correlation_id] = future

        message = aio_pika.Message(
            body=json.dumps(
                {
                    "method": method,
                    "payload": payload
                }
            ).encode(),
            correlation_id=correlation_id,
            reply_to=self.callback_queue.name,
            content_type="application/json"
        )

        await self.channel.default_exchange.publish(
            message,
            routing_key=queue_name
        )

        try:
            response = await asyncio.wait_for(
                future,
                timeout=timeout
            )

            if not isinstance(response, dict):
                raise ValueError(
                    "RPC response must be a dictionary"
                )

            return response

        except asyncio.TimeoutError as error:
            self.futures.pop(
                correlation_id,
                None
            )

            raise ValueError(
                f"RPC service did not respond. "
                f"Queue: {queue_name}, method: {method}"
            ) from error

    async def call_schedule(
        self,
        method: str,
        payload: dict[str, Any],
        timeout: float = 5.0
    ) -> dict[str, Any]:
        return await self.call(
            queue_name=(
                rabbitmq_settings.schedule_rpc_queue
            ),
            method=method,
            payload=payload,
            timeout=timeout
        )

    async def call_academic(
        self,
        method: str,
        payload: dict[str, Any],
        timeout: float = 5.0
    ) -> dict[str, Any]:
        return await self.call(
            queue_name=(
                rabbitmq_settings.academic_rpc_queue
            ),
            method=method,
            payload=payload,
            timeout=timeout
        )

    async def call_user(
        self,
        method: str,
        payload: dict[str, Any],
        timeout: float = 5.0
    ) -> dict[str, Any]:
        return await self.call(
            queue_name=rabbitmq_settings.user_rpc_queue,
            method=method,
            payload=payload,
            timeout=timeout
        )

    async def stop(self) -> None:
        for future in self.futures.values():
            if not future.done():
                future.cancel()

        self.futures.clear()

        self.channel = None
        self.callback_queue = None
        self.started = False

        print(
            "[Content RPC] Client stopped",
            flush=True
        )


rabbit_rpc_client = RabbitRpcClient()