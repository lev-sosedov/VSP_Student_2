from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator
)


# =====================================================
# Базовая схема ссылки
# =====================================================

class LessonLinkBase(BaseModel):
    lesson_content_id: int = Field(
        ...,
        gt=0,
        description="ID основного материала занятия"
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Название ссылки"
    )

    url: HttpUrl = Field(
        ...,
        description="Адрес полезного ресурса"
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
        description="Описание ссылки"
    )

    sort_order: int = Field(
        default=0,
        ge=0,
        description="Порядок отображения"
    )

    is_visible: bool = Field(
        default=True,
        description="Видна ли ссылка студентам"
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
                "Название ссылки не может быть пустым"
            )

        return cleaned_value

    @field_validator("description")
    @classmethod
    def clean_description(
        cls,
        value: str | None
    ) -> str | None:
        if value is None:
            return None

        cleaned_value = value.strip()

        return cleaned_value or None


# =====================================================
# Создание ссылки
# =====================================================

class LessonLinkCreate(LessonLinkBase):
    added_by: int = Field(
        ...,
        gt=0,
        description=(
            "ID пользователя, добавившего ссылку. "
            "Позже будет получаться из JWT"
        )
    )


# =====================================================
# Частичное изменение ссылки
# =====================================================

class LessonLinkUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255
    )

    url: HttpUrl | None = None

    description: str | None = Field(
        default=None,
        max_length=2000
    )

    sort_order: int | None = Field(
        default=None,
        ge=0
    )

    updated_by: int = Field(
        ...,
        gt=0,
        description=(
            "ID пользователя, изменяющего ссылку. "
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
                "Название ссылки не может быть пустым"
            )

        return cleaned_value

    @field_validator("description")
    @classmethod
    def clean_description(
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

class LessonLinkVisibilityRequest(BaseModel):
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

class LessonLinkResponse(BaseModel):
    id: int
    lesson_content_id: int

    title: str
    url: str
    description: str | None

    sort_order: int
    is_visible: bool

    added_by: int

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Список ссылок
# =====================================================

class LessonLinkListResponse(BaseModel):
    total: int
    items: list[LessonLinkResponse]


# =====================================================
# Ответ после удаления
# =====================================================

class LessonLinkDeleteResponse(BaseModel):
    deleted: bool
    link_id: int