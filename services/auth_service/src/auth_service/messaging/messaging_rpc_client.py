"""RabbitMQ RPC client used only by the prepared identity resolver."""

import asyncio
import json
from uuid import uuid4

import aio_pika

from auth_service.messaging.messaging_config import rabbitmq_settings


class UserIdentityRpcClient:
    def __init__(self) -> None:
        self.connection: aio_pika.RobustConnection | None = None
        self.channel: aio_pika.RobustChannel | None = None
        self.callback_queue: aio_pika.RobustQueue | None = None
        self.pending: dict[str, asyncio.Future[dict]] = {}
        self._start_lock = asyncio.Lock()

    async def start(self) -> None:
        async with self._start_lock:
            if self.connection is not None and not self.connection.is_closed:
                return
            self.connection = await aio_pika.connect_robust(
                rabbitmq_settings.url,
                heartbeat=rabbitmq_settings.heartbeat,
            )
            self.channel = await self.connection.channel()
            self.callback_queue = await self.channel.declare_queue(
                exclusive=True,
                auto_delete=True,
            )
            await self.callback_queue.consume(self._on_response, no_ack=True)

    async def _on_response(self, message: aio_pika.IncomingMessage) -> None:
        correlation_id = message.correlation_id
        if correlation_id is None:
            return
        future = self.pending.pop(correlation_id, None)
        if future is not None and not future.done():
            try:
                response = json.loads(message.body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                future.set_exception(RuntimeError("Invalid RPC response"))
            else:
                future.set_result(response)

    async def call(self, method: str, payload: dict) -> dict:
        await self.start()
        if self.channel is None or self.callback_queue is None:
            raise RuntimeError("RPC client is unavailable")

        correlation_id = str(uuid4())
        future = asyncio.get_running_loop().create_future()
        self.pending[correlation_id] = future
        try:
            await self.channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps({"method": method, "payload": payload}).encode(),
                    correlation_id=correlation_id,
                    reply_to=self.callback_queue.name,
                    content_type="application/json",
                ),
                routing_key=rabbitmq_settings.user_rpc_queue,
            )
            return await asyncio.wait_for(
                future,
                timeout=rabbitmq_settings.rpc_timeout_seconds,
            )
        finally:
            self.pending.pop(correlation_id, None)

    async def resolve_by_auth_id(self, auth_user_id: int) -> dict:
        return await self.call(
            "identity.resolve_by_auth_id",
            {"auth_user_id": auth_user_id},
        )

    async def stop(self) -> None:
        for future in self.pending.values():
            if not future.done():
                future.cancel()
        self.pending.clear()

        if self.channel is not None and not self.channel.is_closed:
            await self.channel.close()
        if self.connection is not None and not self.connection.is_closed:
            await self.connection.close()

        self.callback_queue = None
        self.channel = None
        self.connection = None


user_identity_rpc_client = UserIdentityRpcClient()
