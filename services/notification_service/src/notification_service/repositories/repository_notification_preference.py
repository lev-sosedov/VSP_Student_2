from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.models.model_notification_preference import (
    NotificationPreference
)


class NotificationPreferenceRepository:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.session = session

    # =================================================
    # Получить настройки по user_id
    # =================================================

    async def get_by_user_id(
        self,
        user_id: int
    ) -> NotificationPreference | None:
        query = select(NotificationPreference).where(
            NotificationPreference.user_id == user_id
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    # =================================================
    # Создать настройки
    # =================================================

    async def create(
        self,
        user_id: int,
        preference_data: dict
    ) -> NotificationPreference:
        preference = NotificationPreference(
            user_id=user_id,
            **preference_data
        )

        self.session.add(preference)

        await self.session.flush()
        await self.session.refresh(preference)

        return preference

    # =================================================
    # Изменить настройки
    # =================================================

    async def update(
        self,
        preference: NotificationPreference,
        update_data: dict
    ) -> NotificationPreference:
        for field_name, field_value in update_data.items():
            setattr(
                preference,
                field_name,
                field_value
            )

        await self.session.flush()
        await self.session.refresh(preference)

        return preference

    # =================================================
    # Сбросить настройки
    # =================================================

    async def reset(
        self,
        preference: NotificationPreference
    ) -> NotificationPreference:
        preference.in_app_enabled = True
        preference.email_enabled = False
        preference.push_enabled = False
        preference.telegram_enabled = False

        preference.schedule_enabled = True
        preference.lesson_enabled = True
        preference.homework_enabled = True
        preference.homework_result_enabled = True
        preference.chat_enabled = True
        preference.news_enabled = True

        preference.quiet_hours_enabled = False
        preference.quiet_hours_start = None
        preference.quiet_hours_end = None

        preference.timezone = "Europe/Moscow"

        await self.session.flush()
        await self.session.refresh(preference)

        return preference