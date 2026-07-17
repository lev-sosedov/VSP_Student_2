from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator
)

from common.utils.enum_post_media_type import (
    PostMediaType
)


# =====================================================
# Создание медиа
# =====================================================

class PostMediaCreate(BaseModel):
    post_id: int = Field(
        ...,
        gt=0
    )

    media_type: PostMediaType

    file_url: str = Field(
        ...,
        min_length=1,
        max_length=3000
    )

    preview_url: str | None = Field(
        default=None,
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

    width: int | None = Field(
        default=None,
        gt=0
    )

    height: int | None = Field(
        default=None,
        gt=0
    )

    duration_seconds: int | None = Field(
        default=None,
        ge=0
    )

    alt_text: str | None = Field(
        default=None,
        max_length=500
    )

    sort_order: int = Field(
        default=0,
        ge=0
    )

    uploaded_by: int = Field(
        ...,
        gt=0
    )

    @field_validator(
        "file_url",
        "preview_url",
        "file_name",
        "mime_type",
        "alt_text"
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
    def validate_dimensions(self):
        if (
            self.width is None
            and self.height is not None
        ):
            raise ValueError(
                "Для height нужен width"
            )

        if (
            self.width is not None
            and self.height is None
        ):
            raise ValueError(
                "Для width нужен height"
            )

        return self


# =====================================================
# Изменение медиа
# =====================================================

class PostMediaUpdate(BaseModel):
    preview_url: str | None = Field(
        default=None,
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

    width: int | None = Field(
        default=None,
        gt=0
    )

    height: int | None = Field(
        default=None,
        gt=0
    )

    duration_seconds: int | None = Field(
        default=None,
        ge=0
    )

    alt_text: str | None = Field(
        default=None,
        max_length=500
    )

    sort_order: int | None = Field(
        default=None,
        ge=0
    )

    updated_by: int = Field(
        ...,
        gt=0
    )

    @field_validator(
        "preview_url",
        "file_name",
        "mime_type",
        "alt_text"
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
# Действие над медиа
# =====================================================

class PostMediaActionRequest(BaseModel):
    user_id: int = Field(
        ...,
        gt=0
    )


# =====================================================
# Ответ медиа
# =====================================================

class PostMediaResponse(BaseModel):
    id: int
    post_id: int

    media_type: PostMediaType

    file_url: str
    preview_url: str | None

    file_name: str | None
    mime_type: str | None
    file_size: int | None

    width: int | None
    height: int | None
    duration_seconds: int | None

    alt_text: str | None
    sort_order: int

    uploaded_by: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Список медиа
# =====================================================

class PostMediaListResponse(BaseModel):
    total: int
    items: list[PostMediaResponse]


# =====================================================
# Ответ удаления
# =====================================================

class PostMediaDeleteResponse(BaseModel):
    media_id: int
    post_id: int
    deleted: bool