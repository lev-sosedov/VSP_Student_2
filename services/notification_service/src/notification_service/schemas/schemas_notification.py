from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator
)

from common.utils.enum_notification_channel import (
    NotificationChannel
)
from common.utils.enum_notification_priority import (
    NotificationPriority
)
from common.utils.enum_notification_status import (
    NotificationStatus
)
from common.utils.enum_notification_type import (
    NotificationType
)


# =====================================================
# Создание уведомления
# =====================================================

class NotificationCreate(BaseModel):
    notification_type: NotificationType = Field(
        ...,
        description="Категория уведомления"
    )

    priority: NotificationPriority = Field(
        default=NotificationPriority.NORMAL
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=255
    )

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000
    )

    source_service: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    event_type: str = Field(
        ...,
        min_length=1,
        max_length=150
    )

    source_entity_type: str | None = Field(
        default=None,
        max_length=100
    )

    source_entity_id: int | None = Field(
        default=None,
        gt=0
    )

    payload: dict | None = None

    expires_at: datetime | None = None

    user_ids: list[int] = Field(
        ...,
        min_length=1,
        description="ID получателей уведомления"
    )

    channel: NotificationChannel = Field(
        default=NotificationChannel.IN_APP
    )

    @field_validator(
        "title",
        "message",
        "source_service",
        "event_type"
    )
    @classmethod
    def validate_required_text(
        cls,
        value: str
    ) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError(
                "Поле не может быть пустым"
            )

        return cleaned_value

    @field_validator("user_ids")
    @classmethod
    def validate_user_ids(
        cls,
        value: list[int]
    ) -> list[int]:
        cleaned_ids = []

        for user_id in value:
            if user_id <= 0:
                raise ValueError(
                    "ID пользователя должен быть больше нуля"
                )

            if user_id not in cleaned_ids:
                cleaned_ids.append(user_id)

        if not cleaned_ids:
            raise ValueError(
                "Необходимо указать хотя бы одного получателя"
            )

        return cleaned_ids


# =====================================================
# Получатель уведомления
# =====================================================

class NotificationRecipientResponse(BaseModel):
    id: int
    notification_id: int
    user_id: int

    channel: NotificationChannel
    status: NotificationStatus

    delivered_at: datetime | None
    read_at: datetime | None

    error_message: str | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Уведомление пользователя
# =====================================================

class UserNotificationResponse(BaseModel):
    notification_id: int
    recipient_id: int

    notification_type: NotificationType
    priority: NotificationPriority

    title: str
    message: str

    source_service: str
    event_type: str

    source_entity_type: str | None
    source_entity_id: int | None

    payload: dict | None

    channel: NotificationChannel
    status: NotificationStatus

    is_read: bool
    delivered_at: datetime | None
    read_at: datetime | None

    created_at: datetime
    expires_at: datetime | None


# =====================================================
# Список уведомлений пользователя
# =====================================================

class UserNotificationListResponse(BaseModel):
    total: int
    unread_count: int
    items: list[UserNotificationResponse]


# =====================================================
# Ответ после создания
# =====================================================

class NotificationCreateResponse(BaseModel):
    id: int

    notification_type: NotificationType
    priority: NotificationPriority

    title: str
    message: str

    source_service: str
    event_type: str

    source_entity_type: str | None
    source_entity_id: int | None

    payload: dict | None

    created_at: datetime
    expires_at: datetime | None

    recipients: list[NotificationRecipientResponse]

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Запрос прочтения одного уведомления
# =====================================================

class NotificationReadRequest(BaseModel):
    user_id: int = Field(
        ...,
        gt=0,
        description=(
            "ID пользователя. "
            "Позже будет получаться из JWT"
        )
    )


# =====================================================
# Ответ прочтения
# =====================================================

class NotificationReadResponse(BaseModel):
    notification_id: int
    user_id: int

    is_read: bool
    read_at: datetime


# =====================================================
# Ответ счётчика
# =====================================================

class NotificationUnreadCountResponse(BaseModel):
    user_id: int
    unread_count: int


# =====================================================
# Ответ прочтения всех
# =====================================================

class NotificationReadAllResponse(BaseModel):
    user_id: int
    updated_count: int