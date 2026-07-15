from academic_service.messaging.messaging_rpc_client import RabbitRpcClient


class UserRpcClient:

    def __init__(self, rpc_client: RabbitRpcClient):
        self.rpc_client = rpc_client

    async def get_user_by_id(self, user_id: int) -> dict | None:
        response = await self.rpc_client.call(method="user.get_by_id", payload={"user_id": user_id})

        if not response.get("success"):
            raise ValueError(response.get("error", "User Service error"))

        return response.get("user")

    async def get_users_by_ids(self, user_ids: list[int]) -> list[dict]:
        response = await self.rpc_client.call(
            method="users.get_by_ids",
            payload={"user_ids": user_ids}, timeout=15)

        if not response.get("success"):
            raise ValueError(response.get("error", "User Service error"))

        return response.get("users", [])
