"""Typed fail-closed client contract for parent-to-student authorization."""
from collections.abc import Awaitable, Callable
from typing import Any, TypedDict


class ParentStudentAuthorizationResponse(TypedDict, total=False):
    success: bool
    authorized: bool
    parent_user_id: int
    student_user_id: int
    reason: str


RpcCall = Callable[..., Awaitable[Any]]


class ParentAuthorizationClient:
    def __init__(self, rpc_call: RpcCall, timeout: float = 5.0):
        self._rpc_call = rpc_call
        self._timeout = timeout

    async def has_student(self, parent_user_id: int, student_user_id: int) -> bool:
        if (
            isinstance(parent_user_id, bool)
            or isinstance(student_user_id, bool)
            or parent_user_id <= 0
            or student_user_id <= 0
        ):
            return False
        try:
            response = await self._rpc_call(
                "parent.authorization.has_student",
                {
                    "parent_user_id": parent_user_id,
                    "student_user_id": student_user_id,
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
        response_parent = response.get("parent_user_id")
        response_student = response.get("student_user_id")
        if (
            isinstance(response_parent, bool)
            or not isinstance(response_parent, int)
            or response_parent <= 0
            or isinstance(response_student, bool)
            or not isinstance(response_student, int)
            or response_student <= 0
        ):
            return False
        return response_parent == parent_user_id and response_student == student_user_id
