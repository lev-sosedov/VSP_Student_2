"""Role and resource-ownership authorization dependencies."""

from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Depends, HTTPException, Request, status

from common.security.dependencies import get_current_principal
from common.security.exceptions import InsufficientPermissionsError
from common.security.principal import CurrentPrincipal
from common.utils.enum_role import RoleType


OwnerResolver = Callable[[Request], int | Awaitable[int]]


def _forbidden() -> HTTPException:
    error = InsufficientPermissionsError()
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={"code": error.code, "message": error.public_message},
    )


def require_roles(*allowed_roles: RoleType) -> Callable[..., CurrentPrincipal]:
    if not allowed_roles or any(not isinstance(role, RoleType) for role in allowed_roles):
        raise TypeError("require_roles accepts one or more RoleType values")
    allowed = frozenset(allowed_roles)

    def dependency(
        principal: CurrentPrincipal = Depends(get_current_principal),
    ) -> CurrentPrincipal:
        if principal.role not in allowed:
            raise _forbidden()
        return principal

    return dependency


def require_admin() -> Callable[..., CurrentPrincipal]:
    return require_roles(RoleType.ADMIN)


def require_teacher_or_admin() -> Callable[..., CurrentPrincipal]:
    return require_roles(RoleType.TEACHER, RoleType.ADMIN)


def require_self_or_admin(
    owner_id_parameter: str = "user_id",
    *,
    owner_resolver: OwnerResolver | None = None,
) -> Callable[..., Awaitable[CurrentPrincipal]]:
    if not owner_id_parameter and owner_resolver is None:
        raise ValueError("an owner path parameter or resolver is required")

    async def dependency(
        request: Request,
        principal: CurrentPrincipal = Depends(get_current_principal),
    ) -> CurrentPrincipal:
        if principal.role is RoleType.ADMIN:
            return principal
        if owner_resolver is not None:
            owner: Any = owner_resolver(request)
            if hasattr(owner, "__await__"):
                owner = await owner
        else:
            owner = request.path_params.get(owner_id_parameter)
        if isinstance(owner, bool):
            raise _forbidden()
        try:
            owner_id = int(owner)
        except (TypeError, ValueError) as exc:
            raise _forbidden() from exc
        if owner_id <= 0 or owner_id != principal.user_id:
            raise _forbidden()
        return principal

    return dependency
