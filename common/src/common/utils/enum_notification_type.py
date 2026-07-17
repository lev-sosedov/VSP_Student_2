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
    NEWS = "news" # новая новость;

    USER = "user" # изменения аккаунта;
    ACADEMIC = "academic" # группа, курс или учебный план.

    MESSAGE = "message"