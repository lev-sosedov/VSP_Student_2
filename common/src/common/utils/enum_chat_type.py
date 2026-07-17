from enum import StrEnum

# Enum типа чата
class ChatType(StrEnum):
    PRIVATE = "private"
    GROUP = "group"
    LESSON = "lesson"
    SUPPORT = "support"
    CUSTOM = "custom"