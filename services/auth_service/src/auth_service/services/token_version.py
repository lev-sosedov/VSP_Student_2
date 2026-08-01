"""Token-version operations prepared for future session invalidation flows."""

from auth_service.repositories.repository_auth import AuthRepository


class TokenVersionService:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    async def get_current(self, auth_user_id: int) -> int:
        self._validate_auth_user_id(auth_user_id)
        version = await self.repository.get_token_version(auth_user_id)
        if version is None:
            raise LookupError("Authentication user was not found")
        self._validate_version(version)
        return version

    async def invalidate_all_sessions(self, auth_user_id: int) -> int:
        self._validate_auth_user_id(auth_user_id)
        version = await self.repository.increment_token_version(auth_user_id)
        if version is None:
            raise LookupError("Authentication user was not found")
        self._validate_version(version)
        return version

    @staticmethod
    def _validate_auth_user_id(auth_user_id: int) -> None:
        if isinstance(auth_user_id, bool) or not isinstance(auth_user_id, int) or auth_user_id < 1:
            raise ValueError("auth_user_id must be a positive integer")

    @staticmethod
    def _validate_version(version: int) -> None:
        if isinstance(version, bool) or not isinstance(version, int) or version < 1:
            raise ValueError("token_version must be a positive integer")
