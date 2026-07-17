from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)


# =====================================================
# Создание просмотра
# =====================================================

class PostViewCreate(BaseModel):
    user_id: int = Field(
        ...,
        gt=0,
        description=(
            "ID пользователя, открывшего публикацию. "
            "Позже будет получаться из JWT"
        )
    )


# =====================================================
# Ответ просмотра
# =====================================================

class PostViewResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    viewed_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Результат регистрации просмотра
# =====================================================

class PostViewRegistrationResponse(BaseModel):
    post_id: int
    user_id: int

    created: bool
    views_count: int

    view: PostViewResponse


# =====================================================
# Список просмотров
# =====================================================

class PostViewListResponse(BaseModel):
    total: int
    items: list[PostViewResponse]


# =====================================================
# Счётчик просмотров
# =====================================================

class PostViewCountResponse(BaseModel):
    post_id: int
    views_count: int