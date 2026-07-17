from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)


# =====================================================
# Отметить сообщение прочитанным
# =====================================================

class MessageReadCreate(BaseModel):
    user_id: int = Field(
        ...,
        gt=0,
        description=(
            "ID пользователя. "
            "Позже будет получаться из JWT"
        )
    )


# =====================================================
# Отметить чат прочитанным
# =====================================================

class ChatReadAllRequest(BaseModel):
    user_id: int = Field(
        ...,
        gt=0
    )


# =====================================================
# Ответ отметки прочтения
# =====================================================

class MessageReadResponse(BaseModel):
    id: int
    message_id: int
    user_id: int
    read_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Ответ прочтения всего чата
# =====================================================

class ChatReadAllResponse(BaseModel):
    chat_id: int
    user_id: int

    last_read_message_id: int | None
    created_read_count: int


# =====================================================
# Счётчик непрочитанных чата
# =====================================================

class ChatUnreadCountResponse(BaseModel):
    chat_id: int
    user_id: int
    unread_count: int


# =====================================================
# Общий счётчик пользователя
# =====================================================

class UserUnreadCountResponse(BaseModel):
    user_id: int
    unread_count: int