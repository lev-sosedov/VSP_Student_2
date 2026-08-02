from fastapi import Depends, HTTPException, Request, status

from common.security.dependencies import get_current_principal
from common.security.principal import CurrentPrincipal
from common.utils.enum_role import RoleType
from schedule_service.messaging.messaging_rpc_client import rabbit_rpc_client


async def _membership(principal: CurrentPrincipal, group_id: int, role: str) -> CurrentPrincipal:
    if principal.role is RoleType.ADMIN:
        return principal
    try:
        response = await rabbit_rpc_client.call_academic(
            "academic.authorization.membership",
            {"user_id": principal.user_id, "group_id": group_id, "role": role},
            timeout=2.0,
        )
        if not isinstance(response, dict) or response.get("success") is not True or response.get("exists") is not True:
            raise ValueError("authorization denied")
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Group authorization unavailable") from exc
    return principal


async def require_group_student_or_admin(
    request: Request, principal: CurrentPrincipal = Depends(get_current_principal)
) -> CurrentPrincipal:
    return await _membership(principal, int(request.path_params["group_id"]), "student")


async def require_group_teacher_or_admin(
    request: Request, principal: CurrentPrincipal = Depends(get_current_principal)
) -> CurrentPrincipal:
    return await _membership(principal, int(request.path_params["group_id"]), "teacher")


async def require_student_self_or_admin(
    request: Request, principal: CurrentPrincipal = Depends(get_current_principal)
) -> CurrentPrincipal:
    if principal.role is not RoleType.ADMIN and int(request.path_params.get("student_id", 0)) != principal.user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return principal
