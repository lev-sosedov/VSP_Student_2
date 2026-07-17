from enum import StrEnum


# для ленты новостей
# Статус комментария
class PostCommentStatus(StrEnum):
    PUBLISHED = "published"
    HIDDEN = "hidden"
    DELETED = "deleted"