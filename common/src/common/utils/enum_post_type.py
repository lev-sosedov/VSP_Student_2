from enum import StrEnum


# для ленты новостей
# Тип публикации
class PostType(StrEnum):
    POST = "post" # обычная публикация;
    IMPORTANT = "important" # важное объявление;
    EVENT = "event" # мероприятие;
    ACHIEVEMENT = "achievement" # достижение школы или ученика;
    ARTICLE = "article" # большая статья.