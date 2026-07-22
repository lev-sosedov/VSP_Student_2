from datetime import date, datetime, time
from enum import Enum
from typing import Any
from uuid import UUID


# =====================================================
# Преобразование значений для WebSocket JSON
# =====================================================

def serialize_websocket_value(
    value: Any
) -> Any:
    if value is None:
        return None

    if isinstance(value, Enum):
        return value.value

    if isinstance(
        value,
        (
            datetime,
            date,
            time
        )
    ):
        return value.isoformat()

    if isinstance(value, UUID):
        return str(value)

    if isinstance(value, dict):
        return {
            key: serialize_websocket_value(
                nested_value
            )
            for key, nested_value
            in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [
            serialize_websocket_value(item)
            for item in value
        ]

    return value


# =====================================================
# Событие сообщения
# =====================================================

def build_message_event(
    event_type: str,
    message
) -> dict[str, Any]:
    return {
        "event": event_type,
        "data": {
            "id": message.id,
            "chat_id": message.chat_id,
            "sender_id": message.sender_id,

            "message_type": (
                serialize_websocket_value(
                    message.message_type
                )
            ),

            "text": message.text,

            "reply_to_message_id": (
                message.reply_to_message_id
            ),

            "is_edited": message.is_edited,
            "is_deleted": message.is_deleted,
            "is_pinned": message.is_pinned,

            "created_at": (
                serialize_websocket_value(
                    message.created_at
                )
            ),

            "edited_at": (
                serialize_websocket_value(
                    message.edited_at
                )
            ),

            "deleted_at": (
                serialize_websocket_value(
                    message.deleted_at
                )
            )
        }
    }


# =====================================================
# Событие прочтения одного сообщения
# =====================================================

def build_message_read_event(
    chat_id: int,
    message_id: int,
    user_id: int,
    read_at: datetime
) -> dict[str, Any]:
    return {
        "event": "message.read",
        "data": {
            "chat_id": chat_id,
            "message_id": message_id,
            "user_id": user_id,
            "read_at": read_at.isoformat()
        }
    }


# =====================================================
# Событие прочтения всего чата
# =====================================================

def build_chat_read_event(
    chat_id: int,
    user_id: int,
    last_read_message_id: int,
    read_at: datetime
) -> dict[str, Any]:
    return {
        "event": "chat.read",
        "data": {
            "chat_id": chat_id,
            "user_id": user_id,
            "last_read_message_id": (
                last_read_message_id
            ),
            "read_at": read_at.isoformat()
        }
    }


# =====================================================
# Событие присутствия
# =====================================================

def build_presence_event(
    event_type: str,
    chat_id: int,
    user_id: int
) -> dict[str, Any]:
    return {
        "event": event_type,
        "data": {
            "chat_id": chat_id,
            "user_id": user_id
        }
    }


# =====================================================
# Событие набора текста
# =====================================================

def build_typing_event(
    chat_id: int,
    user_id: int,
    is_typing: bool
) -> dict[str, Any]:
    return {
        "event": (
            "typing.started"
            if is_typing
            else "typing.stopped"
        ),
        "data": {
            "chat_id": chat_id,
            "user_id": user_id
        }
    }