from enum import StrEnum


# Enum для уведомлений
# типа уведомления
class NotificationType(StrEnum):
    SYSTEM = "system" # системное уведомление;

    SCHEDULE = "schedule" # изменение расписания;
    LESSON = "lesson" # материалы занятия;

    HOMEWORK = "homework" # новое или изменённое задание;
    HOMEWORK_RESULT = "homework_result" # проверка работы;

    CHAT = "chat" # новое сообщение;
    MESSAGE = "message"

    NEWS = "news" # новая новость;
    COMMENT = "comment"

    USER = "user"
    ACADEMIC = "academic"