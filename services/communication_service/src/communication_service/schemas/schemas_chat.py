from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator
)

from common.utils.enum_chat_type import ChatType


# =====================================================
# Базовая схема чата
# =====================================================

class ChatBase(BaseModel):
    chat_type: ChatType

    title: str | None = Field(
        default=None,
        max_length=255
    )

    description: str | None = Field(
        default=None,
        max_length=5000
    )

    group_id: int | None = Field(
        default=None,
        gt=0
    )

    lesson_id: int | None = Field(
        default=None,
        gt=0
    )

    @field_validator(
        "title",
        "description"
    )
    @classmethod
    def clean_optional_text(
        cls,
        value: str | None
    ) -> str | None:
        if value is None:
            return None

        cleaned_value = value.strip()

        return cleaned_value or None

    @model_validator(mode="after")
    def validate_chat_links(self):
        if self.chat_type == ChatType.GROUP:
            if self.group_id is None:
                raise ValueError(
                    "Для группового чата нужен group_id"
                )

            if self.lesson_id is not None:
                raise ValueError(
                    "У группового чата не должно быть lesson_id"
                )

        if self.chat_type == ChatType.LESSON:
            if self.lesson_id is None:
                raise ValueError(
                    "Для чата занятия нужен lesson_id"
                )

        if self.chat_type == ChatType.PRIVATE:
            if self.group_id is not None:
                raise ValueError(
                    "У личного чата не должно быть group_id"
                )

            if self.lesson_id is not None:
                raise ValueError(
                    "У личного чата не должно быть lesson_id"
                )

        return self


# =====================================================
# Создание чата
# =====================================================

class ChatCreate(ChatBase):
    created_by: int = Field(
        ...,
        gt=0,
        description=(
            "ID создателя. Позже будет получаться из JWT"
        )
    )


# =====================================================
# Частичное изменение чата
# =====================================================

class ChatUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        max_length=255
    )

    description: str | None = Field(
        default=None,
        max_length=5000
    )

    changed_by: int = Field(
        ...,
        gt=0,
        description=(
            "ID пользователя, изменяющего чат. "
            "Позже будет получаться из JWT"
        )
    )

    @field_validator(
        "title",
        "description"
    )
    @classmethod
    def clean_optional_text(
        cls,
        value: str | None
    ) -> str | None:
        if value is None:
            return None

        cleaned_value = value.strip()

        return cleaned_value or None


# =====================================================
# Запрос изменения состояния
# =====================================================

class ChatActionRequest(BaseModel):
    user_id: int = Field(
        ...,
        gt=0
    )


# =====================================================
# Участник в ответе чата
# =====================================================

class ChatMemberShortResponse(BaseModel):
    id: int
    user_id: int
    member_role: str
    is_active: bool
    joined_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Ответ чата
# =====================================================

class ChatResponse(BaseModel):
    id: int
    chat_type: ChatType

    title: str | None
    description: str | None

    group_id: int | None
    lesson_id: int | None

    created_by: int

    is_active: bool
    is_archived: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Последнее сообщение в списке чатов
# =====================================================

class ChatLastMessageResponse(BaseModel):
    id: int
    chat_id: int
    sender_id: int

    text: str | None = None

    is_deleted: bool = False
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Элемент списка чатов
# =====================================================

class ChatListItemResponse(ChatResponse):
    unread_count: int = 0

    last_message: (
        ChatLastMessageResponse | None
    ) = None


# =====================================================
# Подробный ответ чата
# =====================================================

class ChatDetailResponse(ChatResponse):
    members: list[ChatMemberShortResponse]


# =====================================================
# Список чатов
# =====================================================

class ChatListResponse(BaseModel):
    total: int
    items: list[ChatListItemResponse]