from typing import Any

from content_service.messaging.messaging_rpc_client import (
    rabbit_rpc_client
)


def validate_rpc_response(
    response: dict[str, Any],
    service_name: str
) -> None:
    if not response.get("success"):
        error_message = response.get(
            "error",
            "Unknown RPC error"
        )

        raise ValueError(
            f"{service_name}: {error_message}"
        )


async def validate_lesson(
    lesson_id: int
) -> dict[str, Any]:
    response = await rabbit_rpc_client.call_schedule(
        method="lesson.get_by_id",
        payload={
            "lesson_id": lesson_id
        }
    )

    validate_rpc_response(
        response=response,
        service_name="Schedule Service"
    )

    lesson = response.get("lesson")

    if lesson is None:
        raise ValueError(
            "Занятие не найдено"
        )

    if lesson.get("status") == "cancelled":
        raise ValueError(
            "Нельзя создать материал для отменённого занятия"
        )

    return lesson


async def validate_content_author(
    user_id: int
) -> dict[str, Any]:
    response = await rabbit_rpc_client.call_user(
        method="user.get_by_id",
        payload={
            "user_id": user_id
        }
    )

    validate_rpc_response(
        response=response,
        service_name="User Service"
    )

    user = response.get("user")

    if user is None:
        raise ValueError(
            "Пользователь не найден"
        )

    if not user.get("is_active", False):
        raise ValueError(
            "Пользователь неактивен"
        )

    if not user.get(
        "is_account_verified",
        False
    ):
        raise ValueError(
            "Аккаунт пользователя не подтверждён"
        )

    if user.get("role") not in {
        "teacher",
        "admin",
        "TEACHER",
        "ADMIN"
    }:
        raise ValueError(
            "Материалы могут создавать только "
            "преподаватели и администраторы"
        )

    return user

# =====================================================
# Проверка студента
# =====================================================

async def validate_student(
    student_id: int
) -> dict[str, Any]:
    response = await rabbit_rpc_client.call_user(
        method="user.get_by_id",
        payload={
            "user_id": student_id
        }
    )

    validate_rpc_response(
        response=response,
        service_name="User Service"
    )

    user = response.get("user")

    if user is None:
        raise ValueError(
            "Студент не найден"
        )

    if not user.get("is_active", False):
        raise ValueError(
            "Аккаунт студента неактивен"
        )

    if not user.get(
        "is_account_verified",
        False
    ):
        raise ValueError(
            "Аккаунт студента не подтверждён"
        )

    if user.get("role") not in {
        "student",
        "STUDENT"
    }:
        raise ValueError(
            "Пользователь не является студентом"
        )

    return user

# =====================================================
# Проверка участия студента в группе
# =====================================================

async def validate_student_group_membership(
    student_id: int,
    group_id: int
) -> None:
    response = await rabbit_rpc_client.call_academic(
        method="group_member.exists",
        payload={
            "group_id": group_id,
            "user_id": student_id
        }
    )

    validate_rpc_response(
        response=response,
        service_name="Academic Service"
    )

    if not response.get(
        "is_member",
        False
    ):
        raise ValueError(
            "Студент не состоит в группе этого занятия"
        )