"""Reusable method-aware RBAC dependencies for service routers."""

from collections.abc import Callable

from fastapi import Depends, HTTPException, Request, status

from common.security.dependencies import get_optional_principal
from common.security.principal import CurrentPrincipal
from common.utils.enum_role import RoleType


def require_mutation_roles(*roles: RoleType) -> Callable:
    """Allow all authenticated reads; restrict state-changing methods to roles."""
    allowed = set(roles)

    async def dependency(
        request: Request,
        principal: CurrentPrincipal | None = Depends(get_optional_principal),
    ) -> CurrentPrincipal:
        if request.method in {"GET", "HEAD", "OPTIONS"}:
            return principal  # type: ignore[return-value]
        if principal is None or principal.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "insufficient_permissions", "message": "Insufficient permissions"},
            )
        return principal

    return dependency


require_admin_mutations = require_mutation_roles(RoleType.ADMIN)
require_teacher_or_admin_mutations = require_mutation_roles(
    RoleType.TEACHER, RoleType.ADMIN
)


async def require_content_mutation(
    request: Request,
    principal: CurrentPrincipal | None = Depends(get_optional_principal),
) -> CurrentPrincipal:
    """Content writes are teacher/admin, except student-owned submissions."""
    if request.method in {"GET", "HEAD", "OPTIONS"}:
        return principal  # type: ignore[return-value]
    if principal is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    if "/submissions" in request.url.path and principal.role in {
        RoleType.STUDENT, RoleType.ADMIN
    }:
        return principal
    if principal.role not in {RoleType.TEACHER, RoleType.ADMIN}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "insufficient_permissions", "message": "Insufficient permissions"},
        )
    return principal
