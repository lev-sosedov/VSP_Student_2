from common.parent_authorization import ParentAuthorizationClient
from academic_service.messaging.messaging_rpc_client import RabbitRpcClient


class UserRpcClient:

    def __init__(self, rpc_client: RabbitRpcClient):
        self.rpc_client = rpc_client

    async def get_user_by_id(self, user_id: int) -> dict | None:
        response = await self.rpc_client.call(method="user.get_by_id", payload={"user_id": user_id})
        if not isinstance(response, dict) or response.get("success") is not True:
            raise RuntimeError("User Service authorization response unavailable")
        user = response.get("user")
        if user is None:
            return None
        if (
            not isinstance(user, dict)
            or user.get("id") != user_id
            or not isinstance(user.get("role"), str)
            or not isinstance(user.get("is_active"), bool)
        ):
            raise RuntimeError("Malformed User Service authorization response")
        return user

    async def get_users_by_ids(self, user_ids: list[int]) -> list[dict]:
        response = await self.rpc_client.call(
            method="users.get_by_ids",
            payload={"user_ids": user_ids}, timeout=15)
        if not isinstance(response, dict) or response.get("success") is not True:
            raise RuntimeError("User Service profile response unavailable")
        users = response.get("users")
        if not isinstance(users, list):
            raise RuntimeError("Malformed User Service profile response")
        for user in users:
            if (
                not isinstance(user, dict)
                or not isinstance(user.get("id"), int)
                or not isinstance(user.get("role"), str)
                or not isinstance(user.get("is_active"), bool)
            ):
                raise RuntimeError("Malformed User Service profile response")
        return users

    async def has_parent_student_link(self, parent_user_id: int, student_user_id: int) -> bool:
        """Fail-closed check backed by User Service's parent link table."""
        return await ParentAuthorizationClient(self.rpc_client.call).has_student(
            parent_user_id,
            student_user_id,
        )
