from schedule_service.api.api_lesson_schedule import (
    router as lesson_schedule_router
)
from schedule_service.api.api_room import router as room_router
from schedule_service.api.api_schedule_change import (
    router as schedule_change_router
)
from schedule_service.api.api_schedule_template import (
    router as schedule_template_router
)
from schedule_service.api.api_lesson_generation import (
    router as lesson_generation_router
)

__all__ = [
    "room_router",
    "schedule_template_router",
    "lesson_schedule_router",
    "schedule_change_router",
    "lesson_generation_router",
]