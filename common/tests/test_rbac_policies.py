from starlette.requests import Request
import pytest
from fastapi import HTTPException

from common.security.principal import CurrentPrincipal
from common.security.rbac import (
    require_admin_mutations,
    require_content_mutation,
    require_teacher_or_admin_mutations,
)
from common.utils.enum_role import RoleType


def request(method: str, path: str = "/api/v1/resource") -> Request:
    scope = {"type": "http", "method": method, "path": path, "headers": [], "state": {}}
    return Request(scope)


def principal(role: RoleType) -> CurrentPrincipal:
    return CurrentPrincipal(user_id=7, role=role, token_type="access", token_version=1)


@pytest.mark.asyncio
async def test_student_forbidden_on_academic_mutation():
    with pytest.raises(HTTPException) as error:
        await require_admin_mutations(request("POST"), principal(RoleType.STUDENT))
    assert error.value.status_code == 403


@pytest.mark.asyncio
async def test_student_forbidden_on_schedule_mutation():
    with pytest.raises(HTTPException):
        await require_teacher_or_admin_mutations(request("POST"), principal(RoleType.STUDENT))


@pytest.mark.asyncio
async def test_teacher_allowed_schedule_and_content_mutations():
    assert (await require_teacher_or_admin_mutations(request("POST"), principal(RoleType.TEACHER))).role is RoleType.TEACHER
    assert (await require_content_mutation(request("POST"), principal(RoleType.TEACHER))).role is RoleType.TEACHER


@pytest.mark.asyncio
async def test_student_cannot_publish_content_but_can_reach_submission_policy():
    with pytest.raises(HTTPException):
        await require_content_mutation(request("POST", "/api/v1/homeworks/1/publish"), principal(RoleType.STUDENT))
    assert (await require_content_mutation(request("POST", "/api/v1/submissions"), principal(RoleType.STUDENT))).role is RoleType.STUDENT


@pytest.mark.asyncio
async def test_non_admin_forbidden_on_news_mutation():
    with pytest.raises(HTTPException):
        await require_admin_mutations(request("PATCH", "/api/v1/posts/1"), principal(RoleType.TEACHER))


@pytest.mark.asyncio
async def test_public_get_is_allowed_by_method_policy():
    assert await require_admin_mutations(request("GET"), None) is None
