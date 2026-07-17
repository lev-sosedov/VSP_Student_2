from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator
)


# =====================================================
# Базовая схема материала занятия
# =====================================================

class LessonContentBase(BaseModel):
    lesson_id: int = Field(
        ...,
        gt=0,
        description="ID занятия из schedule-service"
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Заголовок материала"
    )

    summary: str | None = Field(
        default=None,
        max_length=1000,
        description="Краткое описание материала"
    )

    content: str | None = Field(
        default=None,
        description="Основной текст материала"
    )

    @field_validator("title")
    @classmethod
    def validate_title(
        cls,
        value: str
    ) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError(
                "Заголовок материала не может быть пустым"
            )

        return cleaned_value

    @field_validator("summary", "content")
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
# Создание материала
# =====================================================

class LessonContentCreate(LessonContentBase):
    created_by: int = Field(
        ...,
        gt=0,
        description=(
            "ID пользователя, создающего материал. "
            "Позже будет получаться из JWT"
        )
    )

    is_published: bool = Field(
        default=False,
        description="Опубликовать материал сразу"
    )


# =====================================================
# Частичное изменение материала
# =====================================================

class LessonContentUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255
    )

    summary: str | None = Field(
        default=None,
        max_length=1000
    )

    content: str | None = None

    updated_by: int = Field(
        ...,
        gt=0,
        description=(
            "ID пользователя, изменяющего материал. "
            "Позже будет получаться из JWT"
        )
    )

    @field_validator("title")
    @classmethod
    def validate_title(
        cls,
        value: str | None
    ) -> str | None:
        if value is None:
            return None

        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError(
                "Заголовок материала не может быть пустым"
            )

        return cleaned_value

    @field_validator("summary", "content")
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
# Публикация или снятие с публикации
# =====================================================

class LessonContentPublicationRequest(BaseModel):
    updated_by: int = Field(
        ...,
        gt=0,
        description=(
            "ID пользователя, изменяющего публикацию. "
            "Позже будет получаться из JWT"
        )
    )


# =====================================================
# Ответ API
# =====================================================

class LessonContentResponse(BaseModel):
    id: int
    lesson_id: int

    title: str
    summary: str | None
    content: str | None

    is_published: bool

    created_by: int
    updated_by: int | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Ответ со списком
# =====================================================

class LessonContentListResponse(BaseModel):
    total: int
    items: list[LessonContentResponse]