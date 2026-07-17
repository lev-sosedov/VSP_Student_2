from enum import StrEnum

# Enum для уведомлений
# Enum статуса доставки
class NotificationStatus(StrEnum):
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"