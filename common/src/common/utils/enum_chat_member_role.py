from enum import StrEnum

# Enum роли участника чата
class ChatMemberRole(StrEnum):
    OWNER = "owner" # создатель чата;
    ADMIN = "admin" # может управлять участниками;
    MEMBER = "member" # обычный участник;
    READ_ONLY = "read_only" # может только читать.