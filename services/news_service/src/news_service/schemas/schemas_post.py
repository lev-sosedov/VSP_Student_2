from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator
)

from common.utils.enum_post_status import (
    PostStatus
)
from common.utils.enum_post_type import (
    PostType
)


# =====================================================
# Базовая схема публикации
# =====================================================

class PostBase(BaseModel):
    post_type: PostType = Field(
        default=PostType.POST
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=500
    )

    slug: str | None = Field(
        default=None,
        max_length=600,
        description=(
            "Адрес публикации. Если не указан, "
            "будет создан автоматически"
        )
    )

    summary: str | None = Field(
        default=None,
        max_length=1500
    )

    content: str | None = Field(
        default=None,
        max_length=100000
    )

    category: str | None = Field(
        default=None,
        max_length=100
    )

    cover_media_url: str | None = Field(
        default=None,
        max_length=3000
    )

    cover_media_type: str | None = Field(
        default=None,
        max_length=50
    )

    cover_preview_url: str | None = Field(
        default=None,
        max_length=3000
    )

    cover_width: int | None = Field(
        default=None,
        gt=0
    )

    cover_height: int | None = Field(
        default=None,
        gt=0
    )

    allow_comments: bool = True
    send_notification: bool = False

    expires_at: datetime | None = None

    @field_validator(
        "title",
        "slug",
        "summary",
        "content",
        "category",
        "cover_media_url",
        "cover_media_type",
        "cover_preview_url"
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
    def validate_cover_dimensions(self):
        if (
            self.cover_width is None
            and self.cover_height is not None
        ):
            raise ValueError(
                "Для cover_height нужен cover_width"
            )

        if (
            self.cover_width is not None
            and self.cover_height is None
        ):
            raise ValueError(
                "Для cover_width нужен cover_height"
            )

        return self


# =====================================================
# Создание публикации
# =====================================================

class PostCreate(PostBase):
    created_by: int = Field(
        ...,
        gt=0,
        description=(
            "ID автора. Позже будет получаться из JWT"
        )
    )


# =====================================================
# Изменение публикации
# =====================================================

class PostUpdate(BaseModel):
    post_type: PostType | None = None

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=500
    )

    slug: str | None = Field(
        default=None,
        min_length=1,
        max_length=600
    )

    summary: str | None = Field(
        default=None,
        max_length=1500
    )

    content: str | None = Field(
        default=None,
        max_length=100000
    )

    category: str | None = Field(
        default=None,
        max_length=100
    )

    cover_media_url: str | None = Field(
        default=None,
        max_length=3000
    )

    cover_media_type: str | None = Field(
        default=None,
        max_length=50
    )

    cover_preview_url: str | None = Field(
        default=None,
        max_length=3000
    )

    cover_width: int | None = Field(
        default=None,
        gt=0
    )

    cover_height: int | None = Field(
        default=None,
        gt=0
    )

    allow_comments: bool | None = None
    send_notification: bool | None = None

    expires_at: datetime | None = None

    updated_by: int = Field(
        ...,
        gt=0,
        description=(
            "ID пользователя, изменяющего публикацию"
        )
    )

    @field_validator(
        "title",
        "slug",
        "summary",
        "content",
        "category",
        "cover_media_url",
        "cover_media_type",
        "cover_preview_url"
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
# Действие над публикацией
# =====================================================

class PostActionRequest(BaseModel):
    user_id: int = Field(
        ...,
        gt=0
    )


# =====================================================
# Публикация
# =====================================================

class PostPublishRequest(BaseModel):
    published_by: int = Field(
        ...,
        gt=0
    )

    send_notification: bool | None = Field(
        default=None,
        description=(
            "Если передано, переопределяет настройку "
            "уведомления перед публикацией"
        )
    )


# =====================================================
# Ответ публикации
# =====================================================

class PostResponse(BaseModel):
    id: int

    post_type: PostType
    status: PostStatus

    title: str
    slug: str

    summary: str | None
    content: str | None
    category: str | None

    cover_media_url: str | None
    cover_media_type: str | None
    cover_preview_url: str | None

    cover_width: int | None
    cover_height: int | None

    created_by: int
    updated_by: int | None
    published_by: int | None

    is_pinned: bool
    is_active: bool

    allow_comments: bool
    send_notification: bool

    views_count: int
    comments_count: int

    published_at: datetime | None
    expires_at: datetime | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Список публикаций
# =====================================================

class PostListResponse(BaseModel):
    total: int
    items: list[PostResponse]