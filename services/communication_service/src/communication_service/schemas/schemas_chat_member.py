from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)

from common.utils.enum_chat_member_role import (
    ChatMemberRole
)


# =====================================================
# Добавление участника
# =====================================================

class ChatMemberCreate(BaseModel):
    chat_id: int = Field(
        ...,
        gt=0
    )

    user_id: int = Field(
        ...,
        gt=0,
        description="ID добавляемого пользователя"
    )

    member_role: ChatMemberRole = Field(
        default=ChatMemberRole.MEMBER
    )

    added_by: int = Field(
        ...,
        gt=0,
        description=(
            "ID пользователя, добавляющего участника. "
            "Позже будет получаться из JWT"
        )
    )


# =====================================================
# Изменение роли
# =====================================================

class ChatMemberRoleUpdate(BaseModel):
    member_role: ChatMemberRole

    changed_by: int = Field(
        ...,
        gt=0,
        description=(
            "ID пользователя, изменяющего роль. "
            "Позже будет получаться из JWT"
        )
    )


# =====================================================
# Действие над участником
# =====================================================

class ChatMemberActionRequest(BaseModel):
    requested_by: int = Field(
        ...,
        gt=0
    )


# =====================================================
# Выход из чата
# =====================================================

class ChatLeaveRequest(BaseModel):
    user_id: int = Field(
        ...,
        gt=0
    )


# =====================================================
# Ответ участника
# =====================================================

class ChatMemberResponse(BaseModel):
    id: int
    chat_id: int
    user_id: int

    member_role: ChatMemberRole

    added_by: int | None
    joined_at: datetime
    left_at: datetime | None

    is_active: bool
    is_muted: bool
    is_pinned: bool

    last_read_message_id: int | None

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Список участников
# =====================================================

class ChatMemberListResponse(BaseModel):
    total: int
    items: list[ChatMemberResponse]