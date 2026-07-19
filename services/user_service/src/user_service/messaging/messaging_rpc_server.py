import json

import aio_pika
from sqlalchemy import select

from user_service.db.db_session import (
    AsyncSessionLocal
)
from user_service.messaging.messaging_config import (
    rabbitmq_settings
)
from user_service.models.model_user import (
    User
)
from user_service.repositories.repository_user import (
    UserRepository
)


class UserRpcServer:
    def __init__(self):
        self.connection: (
            aio_pika.RobustConnection | None
        ) = None

        self.channel: (
            aio_pika.RobustChannel | None
        ) = None

        self.queue: (
            aio_pika.RobustQueue | None
        ) = None

        self.started: bool = False

    # =================================================
    # START
    # =================================================

    async def start(self) -> None:
        if self.started:
            return

        self.connection = (
            await aio_pika.connect_robust(
                rabbitmq_settings.url,
                heartbeat=(
                    rabbitmq_settings.heartbeat
                )
            )
        )

        self.channel = (
            await self.connection.channel()
        )

        await self.channel.set_qos(
            prefetch_count=(
                rabbitmq_settings.prefetch_count
            )
        )

        self.queue = (
            await self.channel.declare_queue(
                rabbitmq_settings.rpc_queue,
                durable=True
            )
        )

        await self.queue.consume(
            self.process_message
        )

        self.started = True

        print(
            "[User RPC] Server started",
            flush=True
        )

    # =================================================
    # PROCESS MESSAGE
    # =================================================

    async def process_message(
        self,
        message: aio_pika.IncomingMessage
    ) -> None:
        async with message.process():
            response = {
                "success": False,
                "error": "Unknown request"
            }

            try:
                request = json.loads(
                    message.body.decode("utf-8")
                )

                method = request.get("method")

                payload = request.get(
                    "payload",
                    {}
                )

                if method == "user.get_by_id":
                    response = (
                        await self.get_user_by_id(
                            payload=payload
                        )
                    )

                elif method == "users.get_by_ids":
                    response = (
                        await self.get_users_by_ids(
                            payload=payload
                        )
                    )

                elif method == "users.get_active_ids":
                    response = (
                        await self.get_active_user_ids(
                            payload=payload
                        )
                    )

                else:
                    response = {
                        "success": False,
                        "error": (
                            "Unknown RPC method: "
                            f"{method}"
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
                await (
                    self.channel
                    .default_exchange
                    .publish(
                        aio_pika.Message(
                            body=json.dumps(
                                response,
                                ensure_ascii=False
                            ).encode("utf-8"),
                            correlation_id=(
                                message.correlation_id
                            ),
                            content_type=(
                                "application/json"
                            )
                        ),
                        routing_key=(
                            message.reply_to
                        )
                    )
                )

    # =================================================
    # GET USER BY ID
    # =================================================

    async def get_user_by_id(
        self,
        payload: dict
    ) -> dict:
        user_id = payload.get("user_id")

        if user_id is None:
            return {
                "success": False,
                "error": "user_id is required"
            }

        try:
            parsed_user_id = int(user_id)

        except (TypeError, ValueError):
            return {
                "success": False,
                "error": "user_id must be integer"
            }

        async with AsyncSessionLocal() as session:
            repository = UserRepository(
                session
            )

            user = await repository.get_by_id(
                parsed_user_id
            )

            if user is None:
                return {
                    "success": True,
                    "user": None
                }

            return {
                "success": True,
                "user": self._serialize_user(
                    user=user
                )
            }

    # =================================================
    # GET USERS BY IDS
    # =================================================

    async def get_users_by_ids(
        self,
        payload: dict
    ) -> dict:
        user_ids = payload.get(
            "user_ids",
            []
        )

        if not isinstance(user_ids, list):
            return {
                "success": False,
                "error": "user_ids must be a list"
            }

        parsed_user_ids: list[int] = []

        for user_id in user_ids:
            try:
                parsed_user_id = int(user_id)

            except (TypeError, ValueError):
                continue

            if (
                parsed_user_id > 0
                and parsed_user_id
                not in parsed_user_ids
            ):
                parsed_user_ids.append(
                    parsed_user_id
                )

        users = []

        async with AsyncSessionLocal() as session:
            repository = UserRepository(
                session
            )

            for user_id in parsed_user_ids:
                user = await repository.get_by_id(
                    user_id
                )

                if user is None:
                    continue

                users.append(
                    self._serialize_user(
                        user=user
                    )
                )

        return {
            "success": True,
            "users": users,
            "total": len(users)
        }

    # =================================================
    # GET ACTIVE VERIFIED USER IDS
    # =================================================

    async def get_active_user_ids(
        self,
        payload: dict
    ) -> dict:
        async with AsyncSessionLocal() as session:
            query = (
                select(User.id)
                .where(
                    User.is_active.is_(True),
                    User.is_account_verified.is_(
                        True
                    )
                )
                .order_by(User.id)
            )

            result = await session.execute(
                query
            )

            user_ids = list(
                result.scalars().all()
            )

        return {
            "success": True,
            "user_ids": user_ids,
            "total": len(user_ids)
        }

    # =================================================
    # SERIALIZE USER
    # =================================================

    def _serialize_user(
        self,
        user
    ) -> dict:
        role = (
            user.role.value
            if hasattr(user.role, "value")
            else str(user.role)
        )

        return {
            "id": user.id,
            "role": role,
            "is_active": user.is_active,
            "is_account_verified": (
                user.is_account_verified
            )
        }

    # =================================================
    # STOP
    # =================================================

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
            "[User RPC] Server stopped",
            flush=True
        )


user_rpc_server = UserRpcServer()