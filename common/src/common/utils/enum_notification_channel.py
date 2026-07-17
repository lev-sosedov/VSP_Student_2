from enum import StrEnum

# Enum для уведомлений
# Enum канала доставки
class NotificationChannel(StrEnum):
    IN_APP = "in_app" # Enum
    EMAIL = "email" # Enum
    PUSH = "push" # Enum
    TELEGRAM = "telegram" # Enum