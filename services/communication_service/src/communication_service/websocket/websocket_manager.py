import asyncio
from collections import defaultdict
from typing import Any

from fastapi import WebSocket


# =====================================================
# WebSocket Manager
# =====================================================

class WebSocketManager:
    def __init__(self):
        # chat_id:
        #   user_id:
        #       set WebSocket-соединений
        #
        # Один пользователь может открыть чат
        # в нескольких вкладках или устройствах.
        self.active_connections: dict[
            int,
            dict[int, set[WebSocket]]
        ] = defaultdict(
            lambda: defaultdict(set)
        )

        self._lock = asyncio.Lock()

    # =================================================
    # Подключение
    # =================================================

    async def connect(
        self,
        chat_id: int,
        user_id: int,
        websocket: WebSocket
    ) -> None:
        await websocket.accept()

        async with self._lock:
            self.active_connections[
                chat_id
            ][
                user_id
            ].add(websocket)

        print(
            f"[WebSocket] User {user_id} connected "
            f"to chat {chat_id}",
            flush=True
        )

    # =================================================
    # Отключение
    # =================================================

    async def disconnect(
        self,
        chat_id: int,
        user_id: int,
        websocket: WebSocket
    ) -> None:
        async with self._lock:
            chat_connections = (
                self.active_connections.get(chat_id)
            )

            if chat_connections is None:
                return

            user_connections = (
                chat_connections.get(user_id)
            )

            if user_connections is None:
                return

            user_connections.discard(websocket)

            if not user_connections:
                chat_connections.pop(
                    user_id,
                    None
                )

            if not chat_connections:
                self.active_connections.pop(
                    chat_id,
                    None
                )

        print(
            f"[WebSocket] User {user_id} disconnected "
            f"from chat {chat_id}",
            flush=True
        )

    # =================================================
    # Отправить конкретному пользователю
    # =================================================

    async def send_to_user(
        self,
        chat_id: int,
        user_id: int,
        event: dict[str, Any]
    ) -> None:
        connections = list(
            self.active_connections
            .get(chat_id, {})
            .get(user_id, set())
        )

        disconnected: list[WebSocket] = []

        for websocket in connections:
            try:
                await websocket.send_json(event)

            except Exception:
                disconnected.append(websocket)

        for websocket in disconnected:
            await self.disconnect(
                chat_id=chat_id,
                user_id=user_id,
                websocket=websocket
            )

    # =================================================
    # Отправить всем участникам чата
    # =================================================

    async def broadcast_to_chat(
        self,
        chat_id: int,
        event: dict[str, Any],
        exclude_user_id: int | None = None
    ) -> None:
        chat_connections = dict(
            self.active_connections.get(
                chat_id,
                {}
            )
        )

        for user_id in chat_connections:
            if (
                exclude_user_id is not None
                and user_id == exclude_user_id
            ):
                continue

            await self.send_to_user(
                chat_id=chat_id,
                user_id=user_id,
                event=event
            )

    # =================================================
    # Количество подключений чата
    # =================================================

    def get_chat_connection_count(
        self,
        chat_id: int
    ) -> int:
        chat_connections = (
            self.active_connections.get(
                chat_id,
                {}
            )
        )

        return sum(
            len(connections)
            for connections
            in chat_connections.values()
        )

    # =================================================
    # Список пользователей онлайн
    # =================================================

    def get_online_user_ids(
        self,
        chat_id: int
    ) -> list[int]:
        chat_connections = (
            self.active_connections.get(
                chat_id,
                {}
            )
        )

        return [
            user_id
            for user_id, connections
            in chat_connections.items()
            if connections
        ]


websocket_manager = WebSocketManager()