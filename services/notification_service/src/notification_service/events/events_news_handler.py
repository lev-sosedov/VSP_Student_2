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


class NewsEventHandler:
    # =================================================
    # Выбор обработчика
    # =================================================

    async def handle(
        self,
        event_type: str,
        payload: dict[str, Any],
        service: NotificationService
    ) -> None:
        handlers = {
            "news.post.published": (
                self.handle_post_published
            ),
            "news.comment.created": (
                self.handle_comment_created
            ),
            "news.comment.reply_created": (
                self.handle_comment_reply_created
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
    # Опубликован новый пост
    # =================================================

    async def handle_post_published(
        self,
        payload: dict[str, Any],
        service: NotificationService
    ) -> None:
        post_id = payload.get("post_id")
        title = payload.get("title")
        published_by = payload.get("published_by")

        if post_id is None or not title:
            raise ValueError(
                "post_id и title обязательны"
            )

        response = await notification_rpc_client.call_user(
            method="users.get_active_ids",
            payload={}
        )

        if not response.get("success"):
            raise ValueError(
                response.get(
                    "error",
                    "Не удалось получить пользователей"
                )
            )

        raw_user_ids = response.get(
            "user_ids",
            []
        )

        user_ids: list[int] = []

        for user_id in raw_user_ids:
            try:
                parsed_user_id = int(user_id)

            except (TypeError, ValueError):
                continue

            if parsed_user_id <= 0:
                continue

            # Автор публикации уже знает,
            # что публикация опубликована.
            if (
                published_by is not None
                and parsed_user_id == int(published_by)
            ):
                continue

            if parsed_user_id not in user_ids:
                user_ids.append(parsed_user_id)

        if not user_ids:
            print(
                f"[Notification] Post {post_id}: "
                f"no recipients",
                flush=True
            )
            return

        summary = payload.get("summary")

        message = (
            str(summary).strip()
            if summary
            else str(title).strip()
        )

        if len(message) > 200:
            message = message[:197] + "..."

        notification_data = NotificationCreate(
            notification_type=NotificationType.NEWS,
            priority=NotificationPriority.NORMAL,
            title="Новая публикация",
            message=message,
            source_service="news-service",
            event_type="news.post.published",
            source_entity_type="post",
            source_entity_id=int(post_id),
            payload=payload,
            user_ids=user_ids,
            channel=NotificationChannel.IN_APP
        )

        await service.create(
            notification_data=notification_data
        )

    # =================================================
    # Новый комментарий к публикации
    # =================================================

    async def handle_comment_created(
        self,
        payload: dict[str, Any],
        service: NotificationService
    ) -> None:
        await self._create_comment_notification(
            payload=payload,
            service=service,
            event_type="news.comment.created",
            title="Новый комментарий",
            default_message=(
                "К вашей публикации добавили комментарий."
            )
        )

    # =================================================
    # Ответ на комментарий
    # =================================================

    async def handle_comment_reply_created(
        self,
        payload: dict[str, Any],
        service: NotificationService
    ) -> None:
        await self._create_comment_notification(
            payload=payload,
            service=service,
            event_type=(
                "news.comment.reply_created"
            ),
            title="Ответ на комментарий",
            default_message=(
                "На ваш комментарий ответили."
            )
        )

    # =================================================
    # Общее создание уведомления комментария
    # =================================================

    async def _create_comment_notification(
        self,
        payload: dict[str, Any],
        service: NotificationService,
        event_type: str,
        title: str,
        default_message: str
    ) -> None:
        comment_id = payload.get("comment_id")
        recipient_user_id = payload.get(
            "recipient_user_id"
        )

        if (
            comment_id is None
            or recipient_user_id is None
        ):
            raise ValueError(
                "comment_id и recipient_user_id "
                "обязательны"
            )

        try:
            recipient_id = int(
                recipient_user_id
            )

        except (TypeError, ValueError) as error:
            raise ValueError(
                "Некорректный recipient_user_id"
            ) from error

        if recipient_id <= 0:
            raise ValueError(
                "Некорректный recipient_user_id"
            )

        text = payload.get("text")

        message = (
            str(text).strip()
            if text
            else default_message
        )

        if len(message) > 200:
            message = message[:197] + "..."

        post_id = payload.get("post_id")

        notification_data = NotificationCreate(
            notification_type=NotificationType.COMMENT,
            priority=NotificationPriority.NORMAL,
            title=title,
            message=message,
            source_service="news-service",
            event_type=event_type,
            source_entity_type="comment",
            source_entity_id=int(comment_id),
            payload={
                **payload,
                "post_id": (
                    int(post_id)
                    if post_id is not None
                    else None
                )
            },
            user_ids=[
                recipient_id
            ],
            channel=NotificationChannel.IN_APP
        )

        await service.create(
            notification_data=notification_data
        )


news_event_handler = NewsEventHandler()