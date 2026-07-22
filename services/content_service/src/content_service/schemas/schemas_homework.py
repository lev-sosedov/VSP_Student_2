from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator
)


# =====================================================
# Базовая схема домашнего задания
# =====================================================

class HomeworkBase(BaseModel):
    lesson_id: int = Field(
        ...,
        gt=0,
        description="ID занятия из schedule-service"
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Название домашнего задания"
    )

    description: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Описание домашнего задания"
    )

    instructions: str | None = Field(
        default=None,
        max_length=10000,
        description="Дополнительные инструкции"
    )

    max_score: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Максимальное количество баллов"
    )

    due_at: datetime | None = Field(
        default=None,
        description="Крайний срок выполнения"
    )

    allow_late_submission: bool = Field(
        default=True,
        description="Разрешена ли сдача после срока"
    )

    @field_validator(
        "title",
        "description"
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

    @field_validator("instructions")
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
# Создание домашнего задания
# =====================================================

class HomeworkCreate(HomeworkBase):
    created_by: int = Field(
        ...,
        gt=0,
        description=(
            "ID преподавателя или администратора. "
            "Позже будет получаться из JWT"
        )
    )

    is_published: bool = Field(
        default=False,
        description="Опубликовать задание сразу"
    )


# =====================================================
# Частичное изменение домашнего задания
# =====================================================

class HomeworkUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255
    )

    description: str | None = Field(
        default=None,
        min_length=1,
        max_length=10000
    )

    instructions: str | None = Field(
        default=None,
        max_length=10000
    )

    max_score: int | None = Field(
        default=None,
        ge=1,
        le=10000
    )

    due_at: datetime | None = None

    allow_late_submission: bool | None = None

    updated_by: int = Field(
        ...,
        gt=0,
        description=(
            "ID пользователя, изменяющего задание. "
            "Позже будет получаться из JWT"
        )
    )

    @field_validator(
        "title",
        "description"
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

    @field_validator("instructions")
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
# Запрос изменения публикации
# =====================================================

class HomeworkPublicationRequest(BaseModel):
    updated_by: int = Field(
        ...,
        gt=0,
        description=(
            "ID пользователя, изменяющего публикацию. "
            "Позже будет получаться из JWT"
        )
    )


# =====================================================
# Запрос изменения активности
# =====================================================

class HomeworkActivityRequest(BaseModel):
    updated_by: int = Field(
        ...,
        gt=0,
        description=(
            "ID пользователя, изменяющего активность. "
            "Позже будет получаться из JWT"
        )
    )


# =====================================================
# Ответ API
# =====================================================

class HomeworkResponse(BaseModel):
    id: int
    lesson_id: int
    group_id: int | None

    title: str
    description: str
    instructions: str | None

    max_score: int
    due_at: datetime | None

    allow_late_submission: bool
    is_published: bool
    is_active: bool

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

class HomeworkListResponse(BaseModel):
    total: int
    items: list[HomeworkResponse]