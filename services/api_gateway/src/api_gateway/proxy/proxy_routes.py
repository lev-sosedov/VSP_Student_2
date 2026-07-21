from api_gateway.core.core_config import settings


SERVICE_URLS: dict[str, str] = settings.service_urls


PUBLIC_ROUTE_SERVICE_MAP: dict[str, str] = {
    # Auth service
    "auth": "auth",

    # User service
    "users": "users",

    # Academic service
    "branch-address": "academic",
    "branches": "academic",
    "directions": "academic",
    "education-plan-modules": "academic",
    "education-plans": "academic",
    "group-members": "academic",
    "groups": "academic",
    "modules": "academic",

    # Schedule service
    "lessons": "schedule",
    "rooms": "schedule",
    "schedule-changes": "schedule",
    "schedule-templates": "schedule",
    "attendance": "schedule",

    # Content service
    "homework-attachments": "content",
    "homeworks": "content",
    "homework-submissions": "content",
    "lesson-attachments": "content",
    "lesson-contents": "content",
    "lesson-links": "content",
    "submission-attachments": "content",

    # Notification service
    "notification-preferences": "notifications",
    "notifications": "notifications",

    # Communication service
    "chat-members": "communication",
    "chats": "communication",
    "message-attachments": "communication",
    "message-reads": "communication",
    "messages": "communication",

    # News service
    "post-comments": "news",
    "post-media": "news",
    "posts": "news",
    "post-views": "news",
}


def get_service_url(service_name: str) -> str | None:
    return SERVICE_URLS.get(service_name)


def get_public_service_name(upstream_path: str) -> str | None:
    normalized_path = upstream_path.strip("/")

    if not normalized_path:
        return None

    resource_name = normalized_path.split("/", maxsplit=1)[0]

    return PUBLIC_ROUTE_SERVICE_MAP.get(resource_name)


def get_public_service_url(upstream_path: str) -> str | None:
    service_name = get_public_service_name(upstream_path)

    if service_name is None:
        return None

    return get_service_url(service_name)