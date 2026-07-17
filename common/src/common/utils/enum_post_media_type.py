from enum import StrEnum


# для ленты новостей
# Тип медиа
class PostMediaType(StrEnum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    LINK = "link"