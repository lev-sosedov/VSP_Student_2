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


def _valid_flags(response: object) -> bool:
    return (
        isinstance(response, dict)
        and isinstance(response.get("success"), bool)
        and isinstance(response.get("authorized"), bool)
        and (response.get("reason") is None or isinstance(response.get("reason"), str))
    )


class ParentAuthorizationClient:
    def __init__(self, rpc_call: RpcCall, timeout: float = 5.0):
        self._rpc_call = rpc_call
        self._timeout = timeout

    async def check(self, parent_user_id: int, student_user_id: int) -> dict[str, Any] | None:
        if not _valid_id(parent_user_id) or not _valid_id(student_user_id):
            return {"success": False, "authorized": False, "reason": "invalid_request"}
        try:
            response = await self._rpc_call(
                "parent.authorization.has_student",
                {"parent_user_id": parent_user_id, "student_user_id": student_user_id},
                timeout=self._timeout,
            )
        except Exception:
            return None
        if not _valid_flags(response):
            return None
        if response["success"] is True and response["authorized"] is True:
            if (
                not _valid_id(response.get("parent_user_id"))
                or not _valid_id(response.get("student_user_id"))
                or response["parent_user_id"] != parent_user_id
                or response["student_user_id"] != student_user_id
            ):
                return None
        return response

    async def has_student(self, parent_user_id: int, student_user_id: int) -> bool:
        response = await self.check(parent_user_id, student_user_id)
        return bool(response and response.get("success") is True and response.get("authorized") is True)


class ParentStudentGroupAuthorizationClient:
    """Validates the cross-service parent > student > group contract."""

    def __init__(self, rpc_call: RpcCall, timeout: float = 5.0):
        self._rpc_call = rpc_call
        self._timeout = timeout

    async def check(self, parent_user_id: int, student_user_id: int, group_id: int) -> dict[str, Any] | None:
        if not all(_valid_id(value) for value in (parent_user_id, student_user_id, group_id)):
            return {"success": False, "authorized": False, "reason": "invalid_request"}
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
            return None
        if not _valid_flags(response):
            return None
        if response["success"] is True and response["authorized"] is True:
            if not all(
                _valid_id(response.get(key)) and response.get(key) == value
                for key, value in (
                    ("parent_user_id", parent_user_id),
                    ("student_user_id", student_user_id),
                    ("group_id", group_id),
                )
            ):
                return None
        return response

    async def has_student_group(self, parent_user_id: int, student_user_id: int, group_id: int) -> bool:
        response = await self.check(parent_user_id, student_user_id, group_id)
        return bool(response and response.get("success") is True and response.get("authorized") is True)