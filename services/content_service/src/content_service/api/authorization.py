from typing import Any

from fastapi import Depends, HTTPException, Request, status
from common.security.dependencies import get_current_principal

from common.security.principal import CurrentPrincipal
from common.utils.enum_role import RoleType
from content_service.messaging.messaging_rpc_client import rabbit_rpc_client
from content_service.db.db_session import AsyncSessionLocal
from content_service.models.model_homework import Homework
from content_service.models.model_homework_submission import HomeworkSubmission


async def lesson_context(lesson_id: int) -> dict[str, Any]:
    """Fetch and strictly validate the schedule authorization context."""
    response = await rabbit_rpc_client.call_schedule(
        "schedule.authorization.lesson_context", {"lesson_id": lesson_id}, timeout=2.0
    )
    if not isinstance(response, dict) or response.get("success") is not True:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Schedule authorization unavailable")
    if response.get("exists") is not True:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    required = ("lesson_id", "group_id", "teacher_id", "status")
    if any(key not in response for key in required):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Malformed lesson authorization response")
    return response


async def require_lesson_role(principal: CurrentPrincipal, lesson_id: int, role: str, *, published: bool = False) -> dict[str, Any]:
    context = await lesson_context(lesson_id)
    if published and context.get("status") in {"cancelled", "completed"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Lesson is not available")
    if principal.role is RoleType.ADMIN:
        return context
    membership = await rabbit_rpc_client.call_academic(
        "academic.authorization.membership",
        {"user_id": principal.user_id, "group_id": context["group_id"], "role": role},
        timeout=2.0,
    )
    if not isinstance(membership, dict) or membership.get("success") is not True or membership.get("exists") is not True or membership.get("is_active") is not True:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Group authorization denied")
    return context


async def require_student_self(principal: CurrentPrincipal, student_id: int) -> None:
    if principal.role is not RoleType.ADMIN and principal.user_id != student_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student identity mismatch")


async def require_content_request(request: Request, principal: CurrentPrincipal = Depends(get_current_principal)) -> CurrentPrincipal:
    """Common fail-closed guard; endpoint handlers perform precise ownership checks."""
    if principal.role is RoleType.ADMIN:
        return principal
    if request.method in {"POST", "PATCH", "PUT", "DELETE"} and "submission" not in request.url.path:
        if principal.role not in {RoleType.TEACHER, RoleType.STUDENT}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    lesson_id = request.query_params.get("lesson_id")
    path = request.url.path
    review = any(action in path for action in ("start-review", "request-revision", "/accept", "/reject"))
    async with AsyncSessionLocal() as session:
        if "submission" in path and request.path_params.get("submission_id"):
            submission = await session.get(HomeworkSubmission, int(request.path_params["submission_id"]))
            if submission is None:
                raise HTTPException(status_code=404, detail="Submission not found")
            if principal.role is RoleType.STUDENT and submission.student_id != principal.user_id:
                raise HTTPException(status_code=403, detail="Submission ownership required")
            homework = await session.get(Homework, submission.homework_id)
            if homework is None:
                raise HTTPException(status_code=404, detail="Homework not found")
            await require_lesson_role(principal, homework.lesson_id, "teacher" if review or principal.role is RoleType.TEACHER else "student", published=False)
        elif request.path_params.get("homework_id"):
            homework = await session.get(Homework, int(request.path_params["homework_id"]))
            if homework is None:
                raise HTTPException(status_code=404, detail="Homework not found")
            await require_lesson_role(principal, homework.lesson_id, "teacher" if principal.role is not RoleType.STUDENT else "student", published=(request.method == "GET"))
        elif lesson_id is not None:
            await require_lesson_role(principal, int(lesson_id), "teacher" if principal.role is not RoleType.STUDENT else "student", published=(request.method == "GET"))
    return principal
