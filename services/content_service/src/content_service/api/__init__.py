from content_service.api.api_homework import (
    router as homework_router
)
from content_service.api.api_homework_attachment import (
    router as homework_attachment_router
)
from content_service.api.api_lesson_attachment import (
    router as lesson_attachment_router
)
from content_service.api.api_lesson_content import (
    router as lesson_content_router
)
from content_service.api.api_lesson_link import (
    router as lesson_link_router
)
from content_service.api.api_homework_submission import (
    router as homework_submission_router
)
from content_service.api.api_submission_attachment import (
    router as submission_attachment_router
)


__all__ = [
    "lesson_content_router",
    "lesson_attachment_router",
    "lesson_link_router",
    "homework_router",
    "homework_attachment_router",
    "homework_submission_router",
    "submission_attachment_router",
]