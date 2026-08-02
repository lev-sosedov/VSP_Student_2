from fastapi import Depends, HTTPException, Request, status

from common.security.dependencies import get_current_principal
from common.security.principal import CurrentPrincipal
from common.utils.enum_role import RoleType
from schedule_service.messaging.messaging_rpc_client import rabbit_rpc_client
from schedule_service.db.db_session import get_session
from schedule_service.models.model_lesson_schedule import LessonSchedule
from schedule_service.models.model_attendance import Attendance
from sqlalchemy import select


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


async def _user_groups(principal: CurrentPrincipal) -> list[int]:
    if principal.role is RoleType.ADMIN:
        return []
    try:
        response = await rabbit_rpc_client.call_academic(
            "academic.authorization.user_groups",
            {"user_id": principal.user_id},
            timeout=2.0,
        )
        group_ids = response.get("group_ids") if isinstance(response, dict) else None
        if response.get("success") is not True or not isinstance(group_ids, list):
            raise ValueError("malformed group authorization response")
        return [int(group_id) for group_id in group_ids if isinstance(group_id, int) and group_id > 0]
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Group authorization unavailable") from exc


async def require_group_student_or_admin(
    request: Request, principal: CurrentPrincipal = Depends(get_current_principal)
) -> CurrentPrincipal:
    return await _membership(principal, int(request.path_params["group_id"]), "student")


async def require_group_teacher_or_admin(
    request: Request, principal: CurrentPrincipal = Depends(get_current_principal)
) -> CurrentPrincipal:
    return await _membership(principal, int(request.path_params["group_id"]), "teacher")


async def require_group_member_or_admin(
    request: Request, principal: CurrentPrincipal = Depends(get_current_principal)
) -> CurrentPrincipal:
    role = "teacher" if principal.role is RoleType.TEACHER else "student"
    return await _membership(principal, int(request.path_params["group_id"]), role)


async def require_student_self_or_admin(
    request: Request, principal: CurrentPrincipal = Depends(get_current_principal)
) -> CurrentPrincipal:
    if principal.role is not RoleType.ADMIN and int(request.path_params.get("student_id", 0)) != principal.user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return principal


async def _lesson(request: Request, principal: CurrentPrincipal, teacher_only: bool, session) -> CurrentPrincipal:
    lesson = await session.get(LessonSchedule, int(request.path_params["lesson_id"]))
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    if principal.role is RoleType.ADMIN:
        return principal
    role = "teacher" if teacher_only else "student"
    return await _membership(principal, lesson.group_id, role)


async def require_lesson_access(request: Request, principal: CurrentPrincipal = Depends(get_current_principal), session=Depends(get_session)) -> CurrentPrincipal:
    return await _lesson(request, principal, False, session)


async def require_lesson_teacher_or_admin(request: Request, principal: CurrentPrincipal = Depends(get_current_principal), session=Depends(get_session)) -> CurrentPrincipal:
    return await _lesson(request, principal, True, session)


async def require_attendance_access(request: Request, principal: CurrentPrincipal = Depends(get_current_principal), session=Depends(get_session)) -> CurrentPrincipal:
    attendance = await session.get(Attendance, int(request.path_params["attendance_id"]))
    if attendance is None:
        raise HTTPException(status_code=404, detail="Attendance not found")
    if principal.role is RoleType.ADMIN or attendance.student_id == principal.user_id:
        return principal
    lesson = await session.get(LessonSchedule, attendance.lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return await _membership(principal, lesson.group_id, "teacher")


async def require_attendance_teacher_or_admin(request: Request, principal: CurrentPrincipal = Depends(get_current_principal), session=Depends(get_session)) -> CurrentPrincipal:
    attendance = await session.get(Attendance, int(request.path_params["attendance_id"]))
    if attendance is None:
        raise HTTPException(status_code=404, detail="Attendance not found")
    if principal.role is RoleType.ADMIN:
        return principal
    lesson = await session.get(LessonSchedule, attendance.lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return await _membership(principal, lesson.group_id, "teacher")
