from enum import StrEnum

# Enum типа вложения сообщения
class MessageAttachmentType(StrEnum):
    FILE = "file"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    OTHER = "other"