from notification_service.api.api_notification import (
    router as notification_router
)
from notification_service.api.api_notification_preference import (
    router as notification_preference_router
)


__all__ = [
    "notification_router",
    "notification_preference_router"
]