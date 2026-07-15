import json
import aio_pika

from user_service.db.db_session import AsyncSessionLocal
from user_service.repositories.repository_user import UserRepository
from user_service.messaging.messaging_config import rabbitmq_settings


class UserRpcServer:

    def __init__(self):
        self.connection: aio_pika.RobustConnection | None = None
        self.channel: aio_pika.RobustChannel | None = None
        self.queue: aio_pika.RobustQueue | None = None

    async def start(self):
        self.connection = await aio_pika.connect_robust(rabbitmq_settings.url, heartbeat=rabbitmq_settings.heartbeat)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=rabbitmq_settings.prefetch_count)
        self.queue = await self.channel.declare_queue(rabbitmq_settings.rpc_queue, durable=True)
        await self.queue.consume(self.process_message)
        print("[User RPC] Server started")

    async def process_message(self, message: aio_pika.IncomingMessage):
        async with message.process():
            response = {"success": False, "error": "Unknown request"}

            try:
                request = json.loads(message.body.decode())

                method = request.get("method")
                payload = request.get("payload", {})

                if method == "user.get_by_id":
                    response = await self.get_user_by_id(payload)

                elif method == "users.get_by_ids":
                    response = await self.get_users_by_ids(payload)

                else:
                    response = {"success": False, "error": f"Unknown RPC method: {method}"}

            except Exception as e:
                response = {"success": False, "error": str(e)}

            if message.reply_to:
                await self.channel.default_exchange.publish(
                    aio_pika.Message(
                        body=json.dumps(response).encode(),
                        correlation_id=message.correlation_id,
                        content_type="application/json"
                    ), routing_key=message.reply_to)

    async def get_user_by_id(self, payload: dict):
        user_id = payload.get("user_id")

        if user_id is None:
            return {"success": False, "error": "user_id is required"}

        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)
            user = await repo.get_by_id(int(user_id))

            if not user:
                return {"success": True, "user": None}

            role = (
                user.role.value
                if hasattr(user.role, "value")
                else str(user.role))

            return {"success": True, "user": {
                "id": user.id,
                "role": role,
                "is_active": user.is_active,
                "is_account_verified": user.is_account_verified}}

    async def get_users_by_ids(self, payload: dict):
        user_ids = payload.get("user_ids", [])

        if not isinstance(user_ids, list):
            return {"success": False, "error": "user_ids must be a list"}

        users = []
        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)

            for user_id in user_ids:
                user = await repo.get_by_id(int(user_id))

                if not user:
                    continue

                role = (
                    user.role.value
                    if hasattr(user.role, "value")
                    else str(user.role))

                users.append({
                    "id": user.id,
                    "role": role,
                    "is_active": user.is_active,
                    "is_account_verified": user.is_account_verified})

        return {"success": True, "users": users}

    async def stop(self):
        if self.channel and not self.channel.is_closed:
            await self.channel.close()

        if self.connection and not self.connection.is_closed:
            await self.connection.close()


user_rpc_server = UserRpcServer()
