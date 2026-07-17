from typing import Any

from news_service.messaging.messaging_rpc_client import (
    news_rpc_client
)


class ExternalValidationService:
    # =================================================
    # Получить активного пользователя
    # =================================================

    async def get_active_user(
        self,
        user_id: int
    ) -> dict[str, Any]:
        response = await news_rpc_client.call_user(
            method="user.get_by_id",
            payload={
                "user_id": user_id
            }
        )

        if not response.get("success"):
            raise ValueError(
                response.get(
                    "error",
                    "Ошибка User Service"
                )
            )

        user = response.get("user")

        if user is None:
            raise ValueError(
                "Пользователь не найден"
            )

        if not user.get("is_active"):
            raise ValueError(
                "Аккаунт пользователя заблокирован"
            )

        if not user.get("is_account_verified"):
            raise ValueError(
                "Аккаунт пользователя не подтверждён"
            )

        return user

    # =================================================
    # Проверка права управления публикациями
    # =================================================

    async def get_content_manager(
        self,
        user_id: int
    ) -> dict[str, Any]:
        user = await self.get_active_user(
            user_id=user_id
        )

        role = str(
            user.get(
                "role",
                ""
            )
        ).lower()

        allowed_roles = {
            "admin",
            "teacher"
        }

        if role not in allowed_roles:
            raise ValueError(
                "У пользователя нет прав "
                "для управления публикациями"
            )

        return user

    # =================================================
    # Проверка права модерации комментариев
    # =================================================

    async def get_comment_moderator(
        self,
        user_id: int
    ) -> dict[str, Any]:
        user = await self.get_active_user(
            user_id=user_id
        )

        role = str(
            user.get(
                "role",
                ""
            )
        ).lower()

        allowed_roles = {
            "admin",
            "teacher"
        }

        if role not in allowed_roles:
            raise ValueError(
                "У пользователя нет прав "
                "для модерации комментариев"
            )

        return user


external_validation_service = (
    ExternalValidationService()
)