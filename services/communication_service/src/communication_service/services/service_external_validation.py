from typing import Any

from communication_service.messaging.messaging_rpc_client import (
    communication_rpc_client
)


class ExternalValidationService:
    # =================================================
    # USER
    # =================================================

    async def get_active_user(
        self,
        user_id: int
    ) -> dict[str, Any]:
        response = await communication_rpc_client.call_user(
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
    # GROUP
    # =================================================

    async def get_group(
        self,
        group_id: int
    ) -> dict[str, Any]:
        response = (
            await communication_rpc_client.call_academic(
                method="group.get_by_id",
                payload={
                    "group_id": group_id
                }
            )
        )

        if not response.get("success"):
            raise ValueError(
                response.get(
                    "error",
                    "Ошибка Academic Service"
                )
            )

        group = response.get("group")

        if group is None:
            raise ValueError(
                "Учебная группа не найдена"
            )

        if not group.get("is_active"):
            raise ValueError(
                "Учебная группа неактивна"
            )

        return group

    # =================================================
    # GROUP MEMBERS
    # =================================================

    async def get_group_members(
        self,
        group_id: int
    ) -> list[dict[str, Any]]:
        response = (
            await communication_rpc_client.call_academic(
                method="group_members.get_by_group",
                payload={
                    "group_id": group_id
                }
            )
        )

        if not response.get("success"):
            raise ValueError(
                response.get(
                    "error",
                    "Ошибка Academic Service"
                )
            )

        return response.get(
            "members",
            []
        )

    # =================================================
    # LESSON
    # =================================================

    async def get_lesson(
        self,
        lesson_id: int
    ) -> dict[str, Any]:
        response = (
            await communication_rpc_client.call_schedule(
                method="lesson.get_by_id",
                payload={
                    "lesson_id": lesson_id
                }
            )
        )

        if not response.get("success"):
            raise ValueError(
                response.get(
                    "error",
                    "Ошибка Schedule Service"
                )
            )

        lesson = response.get("lesson")

        if lesson is None:
            raise ValueError(
                "Занятие не найдено"
            )

        return lesson


external_validation_service = ExternalValidationService()