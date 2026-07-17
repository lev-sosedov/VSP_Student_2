from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    status
)

from communication_service.db.db_session import (
    AsyncSessionLocal
)
from communication_service.repositories.repository_chat import (
    ChatRepository
)
from communication_service.repositories.repository_chat_member import (
    ChatMemberRepository
)
from communication_service.websocket.websocket_events import (
    build_presence_event,
    build_typing_event
)
from communication_service.websocket.websocket_manager import (
    websocket_manager
)


router = APIRouter(
    tags=["WebSocket"]
)


# =====================================================
# Проверка доступа к чату
# =====================================================

async def validate_websocket_access(
    chat_id: int,
    user_id: int
) -> tuple[bool, str | None]:
    async with AsyncSessionLocal() as session:
        chat_repository = ChatRepository(
            session=session
        )

        member_repository = (
            ChatMemberRepository(
                session=session
            )
        )

        chat = await chat_repository.get_by_id(
            chat_id=chat_id
        )

        if chat is None:
            return False, "Чат не найден"

        if not chat.is_active:
            return False, "Чат неактивен"

        member = await member_repository.get_member(
            chat_id=chat_id,
            user_id=user_id
        )

        if member is None or not member.is_active:
            return (
                False,
                "Пользователь не является "
                "активным участником чата"
            )

        return True, None


# =====================================================
# WebSocket чата
# =====================================================

@router.websocket(
    "/ws/chats/{chat_id}"
)
async def chat_websocket_endpoint(
    websocket: WebSocket,
    chat_id: int,
    user_id: int
):
    has_access, error_message = (
        await validate_websocket_access(
            chat_id=chat_id,
            user_id=user_id
        )
    )

    if not has_access:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason=error_message
        )

        return

    await websocket_manager.connect(
        chat_id=chat_id,
        user_id=user_id,
        websocket=websocket
    )

    await websocket_manager.broadcast_to_chat(
        chat_id=chat_id,
        event=build_presence_event(
            event_type="user.online",
            chat_id=chat_id,
            user_id=user_id
        ),
        exclude_user_id=user_id
    )

    try:
        # Сообщаем подключившемуся пользователю,
        # что соединение установлено.
        await websocket.send_json(
            {
                "event": "connection.established",
                "data": {
                    "chat_id": chat_id,
                    "user_id": user_id,
                    "online_user_ids": (
                        websocket_manager
                        .get_online_user_ids(
                            chat_id=chat_id
                        )
                    )
                }
            }
        )

        while True:
            incoming_event = (
                await websocket.receive_json()
            )

            event_type = incoming_event.get(
                "event"
            )

            # Клиент сообщает о наборе текста.
            if event_type == "typing.started":
                await (
                    websocket_manager
                    .broadcast_to_chat(
                        chat_id=chat_id,
                        event=build_typing_event(
                            chat_id=chat_id,
                            user_id=user_id,
                            is_typing=True
                        ),
                        exclude_user_id=user_id
                    )
                )

            elif event_type == "typing.stopped":
                await (
                    websocket_manager
                    .broadcast_to_chat(
                        chat_id=chat_id,
                        event=build_typing_event(
                            chat_id=chat_id,
                            user_id=user_id,
                            is_typing=False
                        ),
                        exclude_user_id=user_id
                    )
                )

            # Проверка активности соединения.
            elif event_type == "ping":
                await websocket.send_json(
                    {
                        "event": "pong",
                        "data": {
                            "chat_id": chat_id
                        }
                    }
                )

            else:
                await websocket.send_json(
                    {
                        "event": "error",
                        "data": {
                            "message": (
                                "Неизвестный тип "
                                "WebSocket-события"
                            )
                        }
                    }
                )

    except WebSocketDisconnect:
        pass

    except Exception as error:
        print(
            f"[WebSocket] Error in chat {chat_id}, "
            f"user {user_id}: {error}",
            flush=True
        )

    finally:
        await websocket_manager.disconnect(
            chat_id=chat_id,
            user_id=user_id,
            websocket=websocket
        )

        await websocket_manager.broadcast_to_chat(
            chat_id=chat_id,
            event=build_presence_event(
                event_type="user.offline",
                chat_id=chat_id,
                user_id=user_id
            ),
            exclude_user_id=user_id
        )