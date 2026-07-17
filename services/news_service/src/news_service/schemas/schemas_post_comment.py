from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator
)

from common.utils.enum_post_comment_status import (
    PostCommentStatus
)


# =====================================================
# Создание комментария
# =====================================================

class PostCommentCreate(BaseModel):
    post_id: int = Field(
        ...,
        gt=0
    )

    author_id: int = Field(
        ...,
        gt=0,
        description=(
            "ID автора. Позже будет получаться из JWT"
        )
    )

    parent_comment_id: int | None = Field(
        default=None,
        gt=0,
        description=(
            "ID родительского комментария, "
            "если это ответ"
        )
    )

    text: str = Field(
        ...,
        min_length=1,
        max_length=10000
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
                "Комментарий не может быть пустым"
            )

        return cleaned_value


# =====================================================
# Изменение комментария
# =====================================================

class PostCommentUpdate(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=10000
    )

    edited_by: int = Field(
        ...,
        gt=0,
        description=(
            "ID пользователя, изменяющего комментарий"
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
                "Комментарий не может быть пустым"
            )

        return cleaned_value


# =====================================================
# Действие над комментарием
# =====================================================

class PostCommentActionRequest(BaseModel):
    requested_by: int = Field(
        ...,
        gt=0
    )


# =====================================================
# Краткий ответ на комментарий
# =====================================================

class PostCommentReplyResponse(BaseModel):
    id: int
    post_id: int
    author_id: int
    parent_comment_id: int | None

    text: str | None
    status: PostCommentStatus

    is_edited: bool

    created_at: datetime
    updated_at: datetime
    edited_at: datetime | None
    deleted_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Ответ комментария
# =====================================================

class PostCommentResponse(BaseModel):
    id: int
    post_id: int
    author_id: int
    parent_comment_id: int | None

    text: str | None
    status: PostCommentStatus

    is_edited: bool

    created_at: datetime
    updated_at: datetime
    edited_at: datetime | None
    deleted_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Подробный комментарий с ответами
# =====================================================

class PostCommentDetailResponse(
    PostCommentResponse
):
    replies: list[
        PostCommentReplyResponse
    ] = []


# =====================================================
# Список комментариев
# =====================================================

class PostCommentListResponse(BaseModel):
    total: int
    items: list[PostCommentDetailResponse]