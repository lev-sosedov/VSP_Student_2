from typing import Any

from common.utils.enum_notification_channel import (
    NotificationChannel
)
from common.utils.enum_notification_priority import (
    NotificationPriority
)
from common.utils.enum_notification_type import (
    NotificationType
)
from notification_service.messaging.messaging_rpc_client import (
    notification_rpc_client
)
from notification_service.schemas.schemas_notification import (
    NotificationCreate
)
from notification_service.services.service_notification import (
    NotificationService
)


class ScheduleEventHandler:
    # =================================================
    # Главный обработчик
    # =================================================

    async def handle(
        self,
        event_type: str,
        payload: dict[str, Any],
        service: NotificationService
    ) -> None:
        handlers = {
            "schedule.lesson.created": (
                self.handle_lesson_created
            ),
            "schedule.lesson.rescheduled": (
                self.handle_lesson_rescheduled
            ),
            "schedule.lesson.cancelled": (
                self.handle_lesson_cancelled
            ),
            "schedule.lesson.teacher_changed": (
                self.handle_teacher_changed
            ),
            "schedule.lesson.room_changed": (
                self.handle_room_changed
            ),
            "schedule.lesson.restored": (
                self.handle_lesson_restored
            )
        }

        handler = handlers.get(event_type)

        if handler is None:
            return

        await handler(
            payload=payload,
            service=service
        )

    # =================================================
    # Получить получателей группы
    # =================================================

    async def get_group_recipient_ids(
        self,
        group_id: int,
        additional_user_ids: list[int | None] | None = None
    ) -> list[int]:
        members_response = (
            await notification_rpc_client.call_academic(
                method="group_members.get_by_group",
                payload={
                    "group_id": group_id
                }
            )
        )

        if not members_response.get("success"):
            raise ValueError(
                members_response.get(
                    "error",
                    "Academic Service вернул ошибку"
                )
            )

        members = members_response.get(
            "members",
            []
        )

        user_ids: list[int] = []

        for member in members:
            role = str(
                member.get("role", "")
            ).lower()

            user_id = member.get("user_id")

            if user_id is None:
                continue

            # Уведомления расписания получают
            # студенты и преподаватели группы.
            if role not in {
                "student",
                "teacher"
            }:
                continue

            user_id = int(user_id)

            if user_id not in user_ids:
                user_ids.append(user_id)

        for user_id in additional_user_ids or []:
            if user_id is None:
                continue

            user_id = int(user_id)

            if user_id > 0 and user_id not in user_ids:
                user_ids.append(user_id)

        return user_ids

    # =================================================
    # Форматирование даты и времени
    # =================================================

    @staticmethod
    def format_lesson_datetime(
        lesson_date: Any,
        start_time: Any,
        end_time: Any
    ) -> str:
        date_text = (
            str(lesson_date)
            if lesson_date is not None
            else "дата не указана"
        )

        start_text = (
            str(start_time)
            if start_time is not None
            else "?"
        )

        end_text = (
            str(end_time)
            if end_time is not None
            else "?"
        )

        return (
            f"{date_text}, "
            f"{start_text}–{end_text}"
        )

    # =================================================
    # Создано занятие
    # =================================================

    async def handle_lesson_created(
        self,
        payload: dict[str, Any],
        service: NotificationService
    ) -> None:
        lesson_id = payload.get("lesson_id")
        group_id = payload.get("group_id")
        teacher_id = payload.get("teacher_id")

        if lesson_id is None or group_id is None:
            raise ValueError(
                "lesson_id и group_id обязательны"
            )

        user_ids = await self.get_group_recipient_ids(
            group_id=int(group_id),
            additional_user_ids=[
                teacher_id
            ]
        )

        if not user_ids:
            print(
                f"[Notification] Для группы {group_id} "
                f"нет получателей",
                flush=True
            )
            return

        lesson_datetime = self.format_lesson_datetime(
            lesson_date=payload.get("lesson_date"),
            start_time=payload.get("start_time"),
            end_time=payload.get("end_time")
        )

        is_extra = bool(
            payload.get("is_extra")
        )

        title = (
            "Добавлено дополнительное занятие"
            if is_extra
            else "Добавлено занятие"
        )

        message = (
            f"{title}: {lesson_datetime}."
        )

        await service.create(
            notification_data=NotificationCreate(
                notification_type=(
                    NotificationType.SCHEDULE
                ),
                priority=(
                    NotificationPriority.HIGH
                    if is_extra
                    else NotificationPriority.NORMAL
                ),
                title=title,
                message=message,
                source_service="schedule-service",
                event_type="schedule.lesson.created",
                source_entity_type="lesson",
                source_entity_id=int(lesson_id),
                payload=payload,
                user_ids=user_ids,
                channel=NotificationChannel.IN_APP
            )
        )

    # =================================================
    # Перенесено занятие
    # =================================================

    async def handle_lesson_rescheduled(
        self,
        payload: dict[str, Any],
        service: NotificationService
    ) -> None:
        lesson_id = payload.get("lesson_id")
        group_id = payload.get("group_id")

        old_teacher_id = payload.get(
            "old_teacher_id"
        )

        new_teacher_id = payload.get(
            "new_teacher_id"
        )

        if lesson_id is None or group_id is None:
            raise ValueError(
                "lesson_id и group_id обязательны"
            )

        user_ids = await self.get_group_recipient_ids(
            group_id=int(group_id),
            additional_user_ids=[
                old_teacher_id,
                new_teacher_id
            ]
        )

        if not user_ids:
            return

        old_datetime = self.format_lesson_datetime(
            lesson_date=payload.get(
                "old_lesson_date"
            ),
            start_time=payload.get(
                "old_start_time"
            ),
            end_time=payload.get(
                "old_end_time"
            )
        )

        new_datetime = self.format_lesson_datetime(
            lesson_date=payload.get(
                "new_lesson_date"
            ),
            start_time=payload.get(
                "new_start_time"
            ),
            end_time=payload.get(
                "new_end_time"
            )
        )

        message = (
            f"Занятие перенесено с "
            f"{old_datetime} на {new_datetime}."
        )

        reason = payload.get("reason")

        if reason:
            message += f" Причина: {reason}"

        await service.create(
            notification_data=NotificationCreate(
                notification_type=(
                    NotificationType.SCHEDULE
                ),
                priority=NotificationPriority.HIGH,
                title="Занятие перенесено",
                message=message,
                source_service="schedule-service",
                event_type=(
                    "schedule.lesson.rescheduled"
                ),
                source_entity_type="lesson",
                source_entity_id=int(lesson_id),
                payload=payload,
                user_ids=user_ids,
                channel=NotificationChannel.IN_APP
            )
        )

    # =================================================
    # Отменено занятие
    # =================================================

    async def handle_lesson_cancelled(
        self,
        payload: dict[str, Any],
        service: NotificationService
    ) -> None:
        lesson_id = payload.get("lesson_id")
        group_id = payload.get("group_id")
        teacher_id = payload.get("teacher_id")

        if lesson_id is None or group_id is None:
            raise ValueError(
                "lesson_id и group_id обязательны"
            )

        user_ids = await self.get_group_recipient_ids(
            group_id=int(group_id),
            additional_user_ids=[
                teacher_id
            ]
        )

        if not user_ids:
            return

        lesson_datetime = self.format_lesson_datetime(
            lesson_date=payload.get("lesson_date"),
            start_time=payload.get("start_time"),
            end_time=payload.get("end_time")
        )

        message = (
            f"Занятие {lesson_datetime} отменено."
        )

        reason = payload.get("reason")

        if reason:
            message += f" Причина: {reason}"

        await service.create(
            notification_data=NotificationCreate(
                notification_type=(
                    NotificationType.SCHEDULE
                ),
                priority=NotificationPriority.URGENT,
                title="Занятие отменено",
                message=message,
                source_service="schedule-service",
                event_type=(
                    "schedule.lesson.cancelled"
                ),
                source_entity_type="lesson",
                source_entity_id=int(lesson_id),
                payload=payload,
                user_ids=user_ids,
                channel=NotificationChannel.IN_APP
            )
        )

    # =================================================
    # Замена преподавателя
    # =================================================

    async def handle_teacher_changed(
        self,
        payload: dict[str, Any],
        service: NotificationService
    ) -> None:
        lesson_id = payload.get("lesson_id")
        group_id = payload.get("group_id")

        old_teacher_id = payload.get(
            "old_teacher_id"
        )

        new_teacher_id = payload.get(
            "new_teacher_id"
        )

        if lesson_id is None or group_id is None:
            raise ValueError(
                "lesson_id и group_id обязательны"
            )

        user_ids = await self.get_group_recipient_ids(
            group_id=int(group_id),
            additional_user_ids=[
                old_teacher_id,
                new_teacher_id
            ]
        )

        if not user_ids:
            return

        lesson_datetime = self.format_lesson_datetime(
            lesson_date=payload.get("lesson_date"),
            start_time=payload.get("start_time"),
            end_time=payload.get("end_time")
        )

        message = (
            f"Для занятия {lesson_datetime} "
            f"назначен другой преподаватель."
        )

        reason = payload.get("reason")

        if reason:
            message += f" Причина: {reason}"

        await service.create(
            notification_data=NotificationCreate(
                notification_type=(
                    NotificationType.SCHEDULE
                ),
                priority=NotificationPriority.HIGH,
                title="Замена преподавателя",
                message=message,
                source_service="schedule-service",
                event_type=(
                    "schedule.lesson.teacher_changed"
                ),
                source_entity_type="lesson",
                source_entity_id=int(lesson_id),
                payload=payload,
                user_ids=user_ids,
                channel=NotificationChannel.IN_APP
            )
        )

    # =================================================
    # Замена кабинета
    # =================================================

    async def handle_room_changed(
        self,
        payload: dict[str, Any],
        service: NotificationService
    ) -> None:
        lesson_id = payload.get("lesson_id")
        group_id = payload.get("group_id")
        teacher_id = payload.get("teacher_id")

        old_room_id = payload.get(
            "old_room_id"
        )

        new_room_id = payload.get(
            "new_room_id"
        )

        if lesson_id is None or group_id is None:
            raise ValueError(
                "lesson_id и group_id обязательны"
            )

        user_ids = await self.get_group_recipient_ids(
            group_id=int(group_id),
            additional_user_ids=[
                teacher_id
            ]
        )

        if not user_ids:
            return

        lesson_datetime = self.format_lesson_datetime(
            lesson_date=payload.get("lesson_date"),
            start_time=payload.get("start_time"),
            end_time=payload.get("end_time")
        )

        message = (
            f"У занятия {lesson_datetime} "
            f"изменён кабинет: "
            f"{old_room_id} → {new_room_id}."
        )

        await service.create(
            notification_data=NotificationCreate(
                notification_type=(
                    NotificationType.SCHEDULE
                ),
                priority=NotificationPriority.HIGH,
                title="Изменён кабинет занятия",
                message=message,
                source_service="schedule-service",
                event_type=(
                    "schedule.lesson.room_changed"
                ),
                source_entity_type="lesson",
                source_entity_id=int(lesson_id),
                payload=payload,
                user_ids=user_ids,
                channel=NotificationChannel.IN_APP
            )
        )

    # =================================================
    # Восстановлено занятие
    # =================================================

    async def handle_lesson_restored(
        self,
        payload: dict[str, Any],
        service: NotificationService
    ) -> None:
        lesson_id = payload.get("lesson_id")
        group_id = payload.get("group_id")
        teacher_id = payload.get("teacher_id")

        if lesson_id is None or group_id is None:
            raise ValueError(
                "lesson_id и group_id обязательны"
            )

        user_ids = await self.get_group_recipient_ids(
            group_id=int(group_id),
            additional_user_ids=[
                teacher_id
            ]
        )

        if not user_ids:
            return

        lesson_datetime = self.format_lesson_datetime(
            lesson_date=payload.get("lesson_date"),
            start_time=payload.get("start_time"),
            end_time=payload.get("end_time")
        )

        await service.create(
            notification_data=NotificationCreate(
                notification_type=(
                    NotificationType.SCHEDULE
                ),
                priority=NotificationPriority.HIGH,
                title="Занятие восстановлено",
                message=(
                    f"Занятие {lesson_datetime} "
                    f"снова включено в расписание."
                ),
                source_service="schedule-service",
                event_type=(
                    "schedule.lesson.restored"
                ),
                source_entity_type="lesson",
                source_entity_id=int(lesson_id),
                payload=payload,
                user_ids=user_ids,
                channel=NotificationChannel.IN_APP
            )
        )


schedule_event_handler = ScheduleEventHandler()