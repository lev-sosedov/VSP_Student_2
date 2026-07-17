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


class ContentEventHandler:
    # =================================================
    # MAIN HANDLER
    # =================================================

    async def handle(
        self,
        event_type: str,
        payload: dict[str, Any],
        service: NotificationService
    ) -> None:
        handlers = {
            "content.homework.published": (
                self.handle_homework_published
            ),
            "content.submission.needs_revision": (
                self.handle_submission_needs_revision
            ),
            "content.submission.accepted": (
                self.handle_submission_accepted
            ),
            "content.submission.rejected": (
                self.handle_submission_rejected
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
    # HOMEWORK PUBLISHED
    # =================================================

    async def handle_homework_published(
        self,
        payload: dict[str, Any],
        service: NotificationService
    ) -> None:
        homework_id = payload.get("homework_id")
        lesson_id = payload.get("lesson_id")

        if homework_id is None or lesson_id is None:
            raise ValueError(
                "homework_id and lesson_id are required"
            )

        lesson_response = (
            await notification_rpc_client.call_schedule(
                method="lesson.get_by_id",
                payload={
                    "lesson_id": lesson_id
                }
            )
        )

        if not lesson_response.get("success"):
            raise ValueError(
                lesson_response.get(
                    "error",
                    "Ошибка Schedule Service"
                )
            )

        lesson = lesson_response.get("lesson")

        if lesson is None:
            raise ValueError(
                "Занятие не найдено"
            )

        group_id = lesson.get("group_id")

        if group_id is None:
            raise ValueError(
                "У занятия отсутствует group_id"
            )

        members_response = (
            await notification_rpc_client.call_academic(
                method="group_members.get_by_group",
                payload={
                    "group_id": group_id,
                    "role": "student"
                }
            )
        )

        if not members_response.get("success"):
            raise ValueError(
                members_response.get(
                    "error",
                    "Ошибка Academic Service"
                )
            )

        members = members_response.get(
            "members",
            []
        )

        user_ids = [
            member["user_id"]
            for member in members
            if member.get("user_id") is not None
        ]

        if not user_ids:
            print(
                f"[Notification] Group {group_id} "
                f"has no active students",
                flush=True
            )
            return

        notification_data = NotificationCreate(
            notification_type=(
                NotificationType.HOMEWORK
            ),
            priority=NotificationPriority.NORMAL,
            title="Новое домашнее задание",
            message=(
                "Преподаватель опубликовал "
                "новое домашнее задание."
            ),
            source_service="content-service",
            event_type="content.homework.published",
            source_entity_type="homework",
            source_entity_id=int(homework_id),
            payload={
                **payload,
                "group_id": group_id
            },
            user_ids=user_ids,
            channel=NotificationChannel.IN_APP
        )

        await service.create(
            notification_data=notification_data
        )

    # =================================================
    # NEEDS REVISION
    # =================================================

    async def handle_submission_needs_revision(
        self,
        payload: dict[str, Any],
        service: NotificationService
    ) -> None:
        student_id = payload.get("student_id")
        submission_id = payload.get("submission_id")

        if student_id is None or submission_id is None:
            raise ValueError(
                "student_id and submission_id are required"
            )

        notification_data = NotificationCreate(
            notification_type=(
                NotificationType.HOMEWORK_RESULT
            ),
            priority=NotificationPriority.HIGH,
            title="Работа возвращена на доработку",
            message=(
                payload.get("teacher_comment")
                or (
                    "Преподаватель вернул работу "
                    "на доработку."
                )
            ),
            source_service="content-service",
            event_type=(
                "content.submission.needs_revision"
            ),
            source_entity_type="submission",
            source_entity_id=int(submission_id),
            payload=payload,
            user_ids=[
                int(student_id)
            ],
            channel=NotificationChannel.IN_APP
        )

        await service.create(
            notification_data=notification_data
        )

    # =================================================
    # ACCEPTED
    # =================================================

    async def handle_submission_accepted(
        self,
        payload: dict[str, Any],
        service: NotificationService
    ) -> None:
        student_id = payload.get("student_id")
        submission_id = payload.get("submission_id")
        score = payload.get("score")

        if student_id is None or submission_id is None:
            raise ValueError(
                "student_id and submission_id are required"
            )

        message = "Домашняя работа принята."

        if score is not None:
            message = (
                f"Домашняя работа принята. "
                f"Результат: {score} баллов."
            )

        notification_data = NotificationCreate(
            notification_type=(
                NotificationType.HOMEWORK_RESULT
            ),
            priority=NotificationPriority.NORMAL,
            title="Домашняя работа принята",
            message=message,
            source_service="content-service",
            event_type=(
                "content.submission.accepted"
            ),
            source_entity_type="submission",
            source_entity_id=int(submission_id),
            payload=payload,
            user_ids=[
                int(student_id)
            ],
            channel=NotificationChannel.IN_APP
        )

        await service.create(
            notification_data=notification_data
        )

    # =================================================
    # REJECTED
    # =================================================

    async def handle_submission_rejected(
        self,
        payload: dict[str, Any],
        service: NotificationService
    ) -> None:
        student_id = payload.get("student_id")
        submission_id = payload.get("submission_id")

        if student_id is None or submission_id is None:
            raise ValueError(
                "student_id and submission_id are required"
            )

        notification_data = NotificationCreate(
            notification_type=(
                NotificationType.HOMEWORK_RESULT
            ),
            priority=NotificationPriority.HIGH,
            title="Домашняя работа отклонена",
            message=(
                payload.get("teacher_comment")
                or "Домашняя работа отклонена."
            ),
            source_service="content-service",
            event_type=(
                "content.submission.rejected"
            ),
            source_entity_type="submission",
            source_entity_id=int(submission_id),
            payload=payload,
            user_ids=[
                int(student_id)
            ],
            channel=NotificationChannel.IN_APP
        )

        await service.create(
            notification_data=notification_data
        )


content_event_handler = ContentEventHandler()