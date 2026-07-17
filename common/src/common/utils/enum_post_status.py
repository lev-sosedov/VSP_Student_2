from enum import StrEnum

# для ленты новостей
# Статус публикации
class PostStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"