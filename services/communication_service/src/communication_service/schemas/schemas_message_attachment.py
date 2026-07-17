from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator
)

from common.utils.enum_message_attachment_type import (
    MessageAttachmentType
)


# =====================================================
# Создание вложения
# =====================================================

class MessageAttachmentCreate(BaseModel):
    message_id: int = Field(
        ...,
        gt=0
    )

    attachment_type: MessageAttachmentType

    file_url: str = Field(
        ...,
        min_length=1,
        max_length=3000
    )

    file_name: str | None = Field(
        default=None,
        max_length=255
    )

    mime_type: str | None = Field(
        default=None,
        max_length=150
    )

    file_size: int | None = Field(
        default=None,
        ge=0,
        description="Размер файла в байтах"
    )

    uploaded_by: int = Field(
        ...,
        gt=0,
        description=(
            "ID пользователя, добавляющего вложение. "
            "Позже будет получаться из JWT"
        )
    )

    @field_validator(
        "file_url",
        "file_name",
        "mime_type"
    )
    @classmethod
    def clean_text(
        cls,
        value: str | None
    ) -> str | None:
        if value is None:
            return None

        cleaned_value = value.strip()

        return cleaned_value or None


# =====================================================
# Запрос удаления
# =====================================================

class MessageAttachmentDeleteRequest(BaseModel):
    requested_by: int = Field(
        ...,
        gt=0
    )


# =====================================================
# Ответ вложения
# =====================================================

class MessageAttachmentResponse(BaseModel):
    id: int
    message_id: int

    attachment_type: MessageAttachmentType

    file_url: str
    file_name: str | None
    mime_type: str | None
    file_size: int | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Список вложений
# =====================================================

class MessageAttachmentListResponse(BaseModel):
    total: int
    items: list[MessageAttachmentResponse]


class MessageAttachmentDeleteResponse(BaseModel):
    attachment_id: int
    message_id: int
    deleted: bool