from typing import Any

from schedule_service.messaging.messaging_rpc_client import (
    rabbit_rpc_client
)


# =====================================================
# RPC response validation
# =====================================================

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


# =====================================================
# Validate branch
# =====================================================

async def validate_branch(
    branch_id: int
) -> dict[str, Any]:
    response = await rabbit_rpc_client.call_academic(
        method="branch.get_by_id",
        payload={
            "branch_id": branch_id
        }
    )

    validate_rpc_response(
        response=response,
        service_name="Academic Service"
    )

    branch = response.get("branch")

    if branch is None:
        raise ValueError(
            "Филиал не найден"
        )

    if not branch.get("is_active", False):
        raise ValueError(
            "Филиал неактивен"
        )

    return branch


# =====================================================
# Validate group
# =====================================================

async def validate_group(
    group_id: int
) -> dict[str, Any]:
    response = await rabbit_rpc_client.call_academic(
        method="group.get_by_id",
        payload={
            "group_id": group_id
        }
    )

    validate_rpc_response(
        response=response,
        service_name="Academic Service"
    )

    group = response.get("group")

    if group is None:
        raise ValueError(
            "Группа не найдена"
        )

    if not group.get("is_active", True):
        raise ValueError(
            "Группа неактивна"
        )

    return group


# =====================================================
# Validate user
# =====================================================

async def validate_user(
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

    return user


# =====================================================
# Validate teacher
# =====================================================

async def validate_teacher(
    teacher_id: int
) -> dict[str, Any]:
    user = await validate_user(
        user_id=teacher_id
    )

    role = user.get("role")

    if role != "teacher":
        raise ValueError(
            "Пользователь не является преподавателем"
        )

    return user


# =====================================================
# Validate group and teacher
# =====================================================

async def validate_group_and_teacher(
    group_id: int,
    teacher_id: int
) -> tuple[dict[str, Any], dict[str, Any]]:
    group = await validate_group(
        group_id=group_id
    )

    teacher = await validate_teacher(
        teacher_id=teacher_id
    )

    return group, teacher


# =====================================================
# Validate room belongs to group branch
# =====================================================

def validate_room_branch(
    room_branch_id: int,
    group: dict[str, Any]
) -> None:
    group_branch_id = group.get("branch_id")

    if group_branch_id is None:
        raise ValueError(
            "У группы не указан филиал"
        )

    if room_branch_id != group_branch_id:
        raise ValueError(
            "Кабинет и группа относятся "
            "к разным филиалам"
        )