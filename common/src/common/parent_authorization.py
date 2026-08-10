"""Typed fail-closed clients for delegated parent authorization."""
from collections.abc import Awaitable, Callable
from typing import Any, TypedDict


class ParentStudentAuthorizationResponse(TypedDict, total=False):
    success: bool
    authorized: bool
    parent_user_id: int
    student_user_id: int
    reason: str


class ParentStudentGroupAuthorizationResponse(TypedDict, total=False):
    success: bool
    authorized: bool
    parent_user_id: int
    student_user_id: int
    group_id: int
    reason: str


RpcCall = Callable[..., Awaitable[Any]]


def _valid_id(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


class ParentAuthorizationClient:
    def __init__(self, rpc_call: RpcCall, timeout: float = 5.0):
        self._rpc_call = rpc_call
        self._timeout = timeout

    async def has_student(self, parent_user_id: int, student_user_id: int) -> bool:
        if not _valid_id(parent_user_id) or not _valid_id(student_user_id):
            return False
        try:
            response = await self._rpc_call(
                "parent.authorization.has_student",
                {"parent_user_id": parent_user_id, "student_user_id": student_user_id},
                timeout=self._timeout,
            )
        except Exception:
            return False
        if not isinstance(response, dict):
            return False
        if not isinstance(response.get("success"), bool):
            return False
        if not isinstance(response.get("authorized"), bool):
            return False
        reason = response.get("reason")
        if reason is not None and not isinstance(reason, str):
            return False
        if response["success"] is not True or response["authorized"] is not True:
            return False
        response_parent = response.get("parent_user_id")
        response_student = response.get("student_user_id")
        return (
            _valid_id(response_parent)
            and _valid_id(response_student)
            and response_parent == parent_user_id
            and response_student == student_user_id
        )


class ParentStudentGroupAuthorizationClient:
    """Validates the cross-service parent > student > group contract."""

    def __init__(self, rpc_call: RpcCall, timeout: float = 5.0):
        self._rpc_call = rpc_call
        self._timeout = timeout

    async def has_student_group(
        self,
        parent_user_id: int,
        student_user_id: int,
        group_id: int,
    ) -> bool:
        if not all(_valid_id(value) for value in (parent_user_id, student_user_id, group_id)):
            return False
        try:
            response = await self._rpc_call(
                "parent.authorization.has_student_group",
                {
                    "parent_user_id": parent_user_id,
                    "student_user_id": student_user_id,
                    "group_id": group_id,
                },
                timeout=self._timeout,
            )
        except Exception:
            return False
        if not isinstance(response, dict):
            return False
        if not isinstance(response.get("success"), bool):
            return False
        if not isinstance(response.get("authorized"), bool):
            return False
        reason = response.get("reason")
        if reason is not None and not isinstance(reason, str):
            return False
        if response["success"] is not True or response["authorized"] is not True:
            return False
        return all(
            response.get(key) == value
            for key, value in (
                ("parent_user_id", parent_user_id),
                ("student_user_id", student_user_id),
                ("group_id", group_id),
            )
        ) and all(_valid_id(response.get(key)) for key in ("parent_user_id", "student_user_id", "group_id"))