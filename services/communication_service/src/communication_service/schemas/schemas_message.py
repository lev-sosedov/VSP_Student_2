from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator
)

from common.utils.enum_message_type import (
    MessageType
)


# =====================================================
# Создание сообщения
# =====================================================

class MessageCreate(BaseModel):
    chat_id: int = Field(
        ...,
        gt=0
    )

    sender_id: int = Field(
        ...,
        gt=0,
        description=(
            "ID отправителя. "
            "Позже будет получаться из JWT"
        )
    )

    message_type: MessageType = Field(
        default=MessageType.TEXT
    )

    text: str | None = Field(
        default=None,
        max_length=20000
    )

    reply_to_message_id: int | None = Field(
        default=None,
        gt=0
    )

    @field_validator("text")
    @classmethod
    def clean_text(
        cls,
        value: str | None
    ) -> str | None:
        if value is None:
            return None

        cleaned_value = value.strip()

        return cleaned_value or None

    @model_validator(mode="after")
    def validate_message_content(self):
        if (
            self.message_type == MessageType.TEXT
            and self.text is None
        ):
            raise ValueError(
                "Текстовое сообщение не может быть пустым"
            )

        return self


# =====================================================
# Изменение сообщения
# =====================================================

class MessageUpdate(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=20000
    )

    edited_by: int = Field(
        ...,
        gt=0,
        description=(
            "ID пользователя, изменяющего сообщение. "
            "Позже будет получаться из JWT"
        )
    )

    @field_validator("text")
    @classmethod
    def clean_text(
        cls,
        value: str
    ) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError(
                "Сообщение не может быть пустым"
            )

        return cleaned_value


# =====================================================
# Действие над сообщением
# =====================================================

class MessageActionRequest(BaseModel):
    requested_by: int = Field(
        ...,
        gt=0
    )


# =====================================================
# Краткое сообщение для ответа
# =====================================================

class ReplyMessageResponse(BaseModel):
    id: int
    sender_id: int
    text: str | None
    is_deleted: bool

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Ответ сообщения
# =====================================================

class MessageResponse(BaseModel):
    id: int
    chat_id: int
    sender_id: int

    message_type: MessageType
    text: str | None

    reply_to_message_id: int | None

    is_edited: bool
    is_deleted: bool
    is_pinned: bool

    created_at: datetime
    edited_at: datetime | None
    deleted_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Подробное сообщение
# =====================================================

class MessageDetailResponse(MessageResponse):
    reply_to: ReplyMessageResponse | None = None


# =====================================================
# Список сообщений
# =====================================================

class MessageListResponse(BaseModel):
    total: int
    items: list[MessageResponse]