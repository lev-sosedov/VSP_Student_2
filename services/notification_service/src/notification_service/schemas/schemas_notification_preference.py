from datetime import datetime, time

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator
)


# =====================================================
# Базовая схема настроек уведомлений
# =====================================================

class NotificationPreferenceBase(BaseModel):
    # Каналы доставки
    in_app_enabled: bool = True
    email_enabled: bool = False
    push_enabled: bool = False
    telegram_enabled: bool = False

    # Категории уведомлений
    schedule_enabled: bool = True
    lesson_enabled: bool = True
    homework_enabled: bool = True
    homework_result_enabled: bool = True
    chat_enabled: bool = True
    news_enabled: bool = True

    # Тихие часы
    quiet_hours_enabled: bool = False

    quiet_hours_start: time | None = None
    quiet_hours_end: time | None = None

    timezone: str = Field(
        default="Europe/Moscow",
        min_length=1,
        max_length=100,
        description="Часовой пояс пользователя"
    )

    # =================================================
    # Проверка тихих часов
    # =================================================

    @model_validator(mode="after")
    def validate_quiet_hours(
        self
    ):
        if self.quiet_hours_enabled:
            if self.quiet_hours_start is None:
                raise ValueError(
                    "Укажите время начала тихих часов"
                )

            if self.quiet_hours_end is None:
                raise ValueError(
                    "Укажите время окончания тихих часов"
                )

        if (
            self.quiet_hours_start is None
            and self.quiet_hours_end is not None
        ):
            raise ValueError(
                "Укажите время начала тихих часов"
            )

        if (
            self.quiet_hours_start is not None
            and self.quiet_hours_end is None
        ):
            raise ValueError(
                "Укажите время окончания тихих часов"
            )

        return self


# =====================================================
# Создание настроек
# =====================================================

class NotificationPreferenceCreate(
    NotificationPreferenceBase
):
    user_id: int = Field(
        ...,
        gt=0,
        description=(
            "ID пользователя из user-service. "
            "Позже будет получаться из JWT"
        )
    )


# =====================================================
# Частичное изменение настроек
# =====================================================

class NotificationPreferenceUpdate(BaseModel):
    in_app_enabled: bool | None = None
    email_enabled: bool | None = None
    push_enabled: bool | None = None
    telegram_enabled: bool | None = None

    schedule_enabled: bool | None = None
    lesson_enabled: bool | None = None
    homework_enabled: bool | None = None
    homework_result_enabled: bool | None = None
    chat_enabled: bool | None = None
    news_enabled: bool | None = None

    quiet_hours_enabled: bool | None = None

    quiet_hours_start: time | None = None
    quiet_hours_end: time | None = None

    timezone: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )


# =====================================================
# Сброс настроек
# =====================================================

class NotificationPreferenceResetRequest(BaseModel):
    requested_by: int = Field(
        ...,
        gt=0,
        description=(
            "ID пользователя, выполняющего сброс. "
            "Позже будет получаться из JWT"
        )
    )


# =====================================================
# Ответ API
# =====================================================

class NotificationPreferenceResponse(BaseModel):
    id: int
    user_id: int

    in_app_enabled: bool
    email_enabled: bool
    push_enabled: bool
    telegram_enabled: bool

    schedule_enabled: bool
    lesson_enabled: bool
    homework_enabled: bool
    homework_result_enabled: bool
    chat_enabled: bool
    news_enabled: bool

    quiet_hours_enabled: bool
    quiet_hours_start: time | None
    quiet_hours_end: time | None

    timezone: str

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )