from datetime import time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.models.model_notification_preference import (
    NotificationPreference
)
from notification_service.repositories.repository_notification_preference import (
    NotificationPreferenceRepository
)
from notification_service.schemas.schemas_notification_preference import (
    NotificationPreferenceCreate,
    NotificationPreferenceUpdate
)


class NotificationPreferenceService:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.repository = NotificationPreferenceRepository(
            session=session
        )

    # =================================================
    # Получить настройки
    # =================================================

    async def get_by_user_id(
        self,
        user_id: int
    ) -> NotificationPreference | None:
        return await self.repository.get_by_user_id(
            user_id=user_id
        )

    # =================================================
    # Получить или создать настройки по умолчанию
    # =================================================

    async def get_or_create_default(
        self,
        user_id: int
    ) -> NotificationPreference:
        preference = await self.repository.get_by_user_id(
            user_id=user_id
        )

        if preference is not None:
            return preference

        return await self.repository.create(
            user_id=user_id,
            preference_data=self._default_values()
        )

    # =================================================
    # Создать настройки
    # =================================================

    async def create(
        self,
        preference_data: NotificationPreferenceCreate
    ) -> NotificationPreference:
        existing_preference = (
            await self.repository.get_by_user_id(
                user_id=preference_data.user_id
            )
        )

        if existing_preference is not None:
            raise ValueError(
                "Настройки уведомлений пользователя "
                "уже созданы"
            )

        self._validate_timezone(
            timezone_name=preference_data.timezone
        )

        self._validate_quiet_hours(
            enabled=preference_data.quiet_hours_enabled,
            start=preference_data.quiet_hours_start,
            end=preference_data.quiet_hours_end
        )

        create_data = preference_data.model_dump(
            exclude={
                "user_id"
            }
        )

        return await self.repository.create(
            user_id=preference_data.user_id,
            preference_data=create_data
        )

    # =================================================
    # Изменить настройки
    # =================================================

    async def update(
        self,
        preference: NotificationPreference,
        preference_data: NotificationPreferenceUpdate
    ) -> NotificationPreference:
        update_data = preference_data.model_dump(
            exclude_unset=True
        )

        timezone_name = update_data.get(
            "timezone",
            preference.timezone
        )

        self._validate_timezone(
            timezone_name=timezone_name
        )

        quiet_hours_enabled = update_data.get(
            "quiet_hours_enabled",
            preference.quiet_hours_enabled
        )

        quiet_hours_start = update_data.get(
            "quiet_hours_start",
            preference.quiet_hours_start
        )

        quiet_hours_end = update_data.get(
            "quiet_hours_end",
            preference.quiet_hours_end
        )

        self._validate_quiet_hours(
            enabled=quiet_hours_enabled,
            start=quiet_hours_start,
            end=quiet_hours_end
        )

        return await self.repository.update(
            preference=preference,
            update_data=update_data
        )

    # =================================================
    # Сбросить настройки
    # =================================================

    async def reset(
        self,
        preference: NotificationPreference,
        requested_by: int
    ) -> NotificationPreference:
        if preference.user_id != requested_by:
            raise ValueError(
                "Нельзя сбросить настройки "
                "другого пользователя"
            )

        return await self.repository.reset(
            preference=preference
        )

    # =================================================
    # Проверка часового пояса
    # =================================================

    @staticmethod
    def _validate_timezone(
        timezone_name: str
    ) -> None:
        try:
            ZoneInfo(timezone_name)

        except ZoneInfoNotFoundError as error:
            raise ValueError(
                "Указан неизвестный часовой пояс"
            ) from error

    # =================================================
    # Проверка тихих часов
    # =================================================

    @staticmethod
    def _validate_quiet_hours(
        enabled: bool,
        start: time | None,
        end: time | None
    ) -> None:
        if enabled:
            if start is None or end is None:
                raise ValueError(
                    "Для тихих часов необходимо указать "
                    "время начала и окончания"
                )

        if start is None and end is not None:
            raise ValueError(
                "Укажите время начала тихих часов"
            )

        if start is not None and end is None:
            raise ValueError(
                "Укажите время окончания тихих часов"
            )

    # =================================================
    # Значения по умолчанию
    # =================================================

    @staticmethod
    def _default_values() -> dict:
        return {
            "in_app_enabled": True,
            "email_enabled": False,
            "push_enabled": False,
            "telegram_enabled": False,

            "schedule_enabled": True,
            "lesson_enabled": True,
            "homework_enabled": True,
            "homework_result_enabled": True,
            "chat_enabled": True,
            "news_enabled": True,

            "quiet_hours_enabled": False,
            "quiet_hours_start": None,
            "quiet_hours_end": None,

            "timezone": "Europe/Moscow"
        }