from enum import StrEnum


class AttachmentType(StrEnum):
    DOCUMENT = "document"
    PRESENTATION = "presentation"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    CODE = "code"
    OTHER = "other"