import asyncio
import json
import uuid
import aio_pika

from academic_service.messaging.messaging_rabbit import RabbitConnection
from academic_service.messaging.messaging_config import rabbitmq_settings


class RabbitRpcClient:

    def __init__(self):
        self.channel: aio_pika.RobustChannel | None = None
        self.callback_queue: aio_pika.RobustQueue | None = None
        self.futures: dict[str, asyncio.Future] = {}
        self.started = False

    async def start(self):
        if self.started:
            return

        self.channel = await RabbitConnection.get_channel()
        self.callback_queue = await self.channel.declare_queue(exclusive=True, auto_delete=True)
        await self.callback_queue.consume(self.on_response, no_ack=True)
        self.started = True
        print("[Academic RPC] Client started")

    async def on_response(self, message: aio_pika.IncomingMessage):
        correlation_id = message.correlation_id

        if not correlation_id:
            return

        future = self.futures.pop(correlation_id, None)

        if not future or future.done():
            return

        try:
            response = json.loads(message.body.decode())
            future.set_result(response)

        except Exception as e:
            future.set_exception(e)

    async def call(self, method: str, payload: dict, timeout: float = 5.0) -> dict:
        if not self.started:
            await self.start()

        correlation_id = str(uuid.uuid4())

        loop = asyncio.get_running_loop()
        future = loop.create_future()

        self.futures[correlation_id] = future

        message = aio_pika.Message(
            body=json.dumps({
                "method": method,
                "payload": payload
            }).encode(),
            correlation_id=correlation_id,
            reply_to=self.callback_queue.name,
            content_type="application/json")

        await self.channel.default_exchange.publish(message, routing_key=rabbitmq_settings.rpc_queue)

        try:
            return await asyncio.wait_for(future, timeout=timeout)

        except asyncio.TimeoutError:
            self.futures.pop(correlation_id, None)

            raise ValueError("User Service did not respond")


rabbit_rpc_client = RabbitRpcClient()
