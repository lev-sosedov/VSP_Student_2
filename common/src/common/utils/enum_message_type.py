from enum import StrEnum

# Enum типа сообщения
class MessageType(StrEnum):
    TEXT = "text"
    SYSTEM = "system"
    FILE = "file"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"