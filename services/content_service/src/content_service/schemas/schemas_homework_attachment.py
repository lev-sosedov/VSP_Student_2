from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator
)

from common.utils.enum_attachment_type import AttachmentType


# =====================================================
# Базовая схема вложения домашнего задания
# =====================================================

class HomeworkAttachmentBase(BaseModel):
    homework_id: int = Field(
        ...,
        gt=0,
        description="ID домашнего задания"
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Название вложения"
    )

    attachment_type: AttachmentType = Field(
        ...,
        description="Тип вложения"
    )

    file_url: str = Field(
        ...,
        min_length=1,
        max_length=3000,
        description="URL файла в объектном хранилище"
    )

    file_name: str | None = Field(
        default=None,
        max_length=255,
        description="Исходное имя файла"
    )

    mime_type: str | None = Field(
        default=None,
        max_length=150,
        description="MIME-тип файла"
    )

    file_size: int | None = Field(
        default=None,
        ge=0,
        description="Размер файла в байтах"
    )

    sort_order: int = Field(
        default=0,
        ge=0,
        description="Порядок отображения"
    )

    is_visible: bool = Field(
        default=True,
        description="Видно ли вложение студентам"
    )

    @field_validator(
        "title",
        "file_url"
    )
    @classmethod
    def validate_required_text(
        cls,
        value: str
    ) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError(
                "Поле не может быть пустым"
            )

        return cleaned_value

    @field_validator(
        "file_name",
        "mime_type"
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
# Создание вложения
# =====================================================

class HomeworkAttachmentCreate(
    HomeworkAttachmentBase
):
    uploaded_by: int = Field(
        ...,
        gt=0,
        description=(
            "ID преподавателя или администратора. "
            "Позже будет получаться из JWT"
        )
    )


# =====================================================
# Частичное изменение вложения
# =====================================================

class HomeworkAttachmentUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255
    )

    attachment_type: AttachmentType | None = None

    file_url: str | None = Field(
        default=None,
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
        ge=0
    )

    sort_order: int | None = Field(
        default=None,
        ge=0
    )

    updated_by: int = Field(
        ...,
        gt=0,
        description=(
            "ID пользователя, изменяющего вложение. "
            "Позже будет получаться из JWT"
        )
    )

    @field_validator(
        "title",
        "file_url"
    )
    @classmethod
    def validate_required_text(
        cls,
        value: str | None
    ) -> str | None:
        if value is None:
            return None

        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError(
                "Поле не может быть пустым"
            )

        return cleaned_value

    @field_validator(
        "file_name",
        "mime_type"
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
# Изменение видимости
# =====================================================

class HomeworkAttachmentVisibilityRequest(
    BaseModel
):
    updated_by: int = Field(
        ...,
        gt=0,
        description=(
            "ID пользователя, изменяющего видимость. "
            "Позже будет получаться из JWT"
        )
    )


# =====================================================
# Ответ API
# =====================================================

class HomeworkAttachmentResponse(BaseModel):
    id: int
    homework_id: int

    title: str
    attachment_type: AttachmentType

    file_url: str
    file_name: str | None
    mime_type: str | None
    file_size: int | None

    sort_order: int
    is_visible: bool

    uploaded_by: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Список вложений
# =====================================================

class HomeworkAttachmentListResponse(BaseModel):
    total: int
    items: list[HomeworkAttachmentResponse]


# =====================================================
# Ответ после удаления
# =====================================================

class HomeworkAttachmentDeleteResponse(BaseModel):
    deleted: bool
    attachment_id: int