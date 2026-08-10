import os
from pathlib import Path
from types import SimpleNamespace
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("RABBITMQ_USERNAME", "test")
os.environ.setdefault("RABBITMQ_PASSWORD", "test")

import pytest
from fastapi import HTTPException

from common.security.principal import CurrentPrincipal
from common.utils.enum_role import RoleType
from schedule_service.api import api_attendance as attendance_module
from schedule_service.api import api_lesson_schedule as lesson_module
from schedule_service.api.authorization import require_parent_student, require_parent_student_group


def principal(user_id=10, role=RoleType.PARENT):
    return CurrentPrincipal(user_id=user_id, role=role, token_type="access", token_version=1)


@pytest.mark.asyncio
async def test_parent_group_authorization_allows_linked_student(monkeypatch):
    async def call_user(_method, _payload, **_kwargs):
        return {"success": True, "authorized": True, "parent_user_id": 10, "student_user_id": 20}

    monkeypatch.setattr("schedule_service.api.authorization.rabbit_rpc_client.call_user", call_user)
    assert await require_parent_student(principal(), 20) is not None


@pytest.mark.asyncio
async def test_parent_group_authorization_denies_foreign_student(monkeypatch):
    async def call_user(_method, _payload, **_kwargs):
        return {"success": True, "authorized": False, "reason": "parent_student_link_not_found"}

    monkeypatch.setattr("schedule_service.api.authorization.rabbit_rpc_client.call_user", call_user)
    with pytest.raises(HTTPException) as error:
        await require_parent_student(principal(), 21)
    assert error.value.status_code == 403


@pytest.mark.asyncio
async def test_parent_group_authorization_unavailable_is_503(monkeypatch):
    async def call_academic(_method, _payload, **_kwargs):
        return None

    monkeypatch.setattr("schedule_service.api.authorization.rabbit_rpc_client.call_academic", call_academic)
    with pytest.raises(HTTPException) as error:
        await require_parent_student_group(principal(), 20, 30)
    assert error.value.status_code == 503


@pytest.mark.asyncio
async def test_parent_attendance_endpoint_filters_by_child_and_group(monkeypatch):
    async def authorize(_principal, student_id, group_id):
        assert student_id == 20
        assert group_id == 30

    async def records(**kwargs):
        assert kwargs["student_id"] == 20
        assert kwargs["group_id"] == 30
        return [], 0

    monkeypatch.setattr(attendance_module, "require_parent_student_group", authorize)
    monkeypatch.setattr(attendance_module, "get_attendance_records", records)
    result = await attendance_module.get_parent_child_attendance_endpoint(
        20, 30, 0, 100, SimpleNamespace(), principal()
    )
    assert result.total == 0
    assert result.items == []


@pytest.mark.asyncio
async def test_parent_attendance_foreign_child_is_denied(monkeypatch):
    async def authorize(*_args):
        raise HTTPException(status_code=403, detail="Forbidden")

    monkeypatch.setattr(attendance_module, "require_parent_student", authorize)
    with pytest.raises(HTTPException) as error:
        await attendance_module.get_parent_child_attendance_endpoint(
            21, None, 0, 100, SimpleNamespace(), principal()
        )
    assert error.value.status_code == 403


@pytest.mark.asyncio
async def test_parent_schedule_endpoint_filters_authorized_group(monkeypatch):
    async def authorize(_principal, student_id, group_id):
        assert student_id == 20
        assert group_id == 30

    async def lessons(**kwargs):
        assert kwargs["group_id"] == 30
        return [], 0

    monkeypatch.setattr(lesson_module, "require_parent_student_group", authorize)
    monkeypatch.setattr(lesson_module, "get_lessons", lessons)
    result = await lesson_module.get_parent_child_group_lessons_endpoint(
        20, 30, None, None, SimpleNamespace(), principal()
    )
    assert result.total == 0
    assert result.items == []


def test_schedule_parent_endpoints_and_mutation_guards_are_explicit():
    attendance = Path("services/schedule_service/src/schedule_service/api/api_attendance.py").read_text(encoding="utf-8")
    lessons = Path("services/schedule_service/src/schedule_service/api/api_lesson_schedule.py").read_text(encoding="utf-8")
    assert '"/parent/children/{student_id}"' in attendance
    assert '"/parent/children/{student_id}/groups/{group_id}"' in lessons
    assert "require_parent_student_group" in attendance
    assert "require_parent_student_group" in lessons
    assert "require_lesson_teacher_or_admin" in lessons
    assert "require_attendance_teacher_or_admin" in attendance
    assert "create_attendance_endpoint" in attendance


def test_attendance_group_filter_is_server_side():
    source = Path("services/schedule_service/src/schedule_service/services/service_attendance.py").read_text(encoding="utf-8")
    assert "Attendance.lesson_id.in_" in source
    assert "LessonSchedule.group_id == group_id" in source