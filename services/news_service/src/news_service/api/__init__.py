from news_service.api.api_post import (
    router as post_router
)
from news_service.api.api_post_media import (
    router as post_media_router
)
from news_service.api.api_post_view import (
    router as post_view_router
)
from news_service.api.api_post_comment import (
    router as post_comment_router
)


__all__ = [
    "post_router",
    "post_media_router",
    "post_view_router",
"post_comment_router",
]