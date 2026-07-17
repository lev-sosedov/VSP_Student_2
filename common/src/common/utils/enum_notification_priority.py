from enum import StrEnum

# Enum для уведомлений
# Enum приоритета
class NotificationPriority(StrEnum):
    LOW = "low" # новая новость;
    NORMAL = "normal" # опубликован материал;
    HIGH = "high" # перенесено занятие;
    URGENT = "urgent" # занятие отменено сегодня.