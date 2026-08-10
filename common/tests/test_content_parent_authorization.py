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
from content_service.api import api_homework as homework_module
from content_service.api import api_homework_submission as submission_module
from content_service.api.authorization import require_parent_student_group


def parent(user_id=10):
    return CurrentPrincipal(user_id=user_id, role=RoleType.PARENT, token_type="access", token_version=1)


@pytest.mark.asyncio
async def test_parent_linked_group_is_authorized(monkeypatch):
    async def call(_method, _payload, **_kwargs):
        return {"success": True, "authorized": True, "parent_user_id": 10, "student_user_id": 20, "group_id": 30}
    monkeypatch.setattr("content_service.api.authorization.rabbit_rpc_client.call_academic", call)
    await require_parent_student_group(parent(), 20, 30)


@pytest.mark.asyncio
async def test_parent_foreign_group_is_forbidden(monkeypatch):
    async def call(_method, _payload, **_kwargs):
        return {"success": True, "authorized": False, "reason": "parent_student_group_link_not_found"}
    monkeypatch.setattr("content_service.api.authorization.rabbit_rpc_client.call_academic", call)
    with pytest.raises(HTTPException) as error:
        await require_parent_student_group(parent(), 21, 30)
    assert error.value.status_code == 403


@pytest.mark.asyncio
async def test_parent_rpc_failure_is_fail_closed(monkeypatch):
    async def call(_method, _payload, **_kwargs):
        return None
    monkeypatch.setattr("content_service.api.authorization.rabbit_rpc_client.call_academic", call)
    with pytest.raises(HTTPException) as error:
        await require_parent_student_group(parent(), 20, 30)
    assert error.value.status_code == 503


@pytest.mark.asyncio
async def test_homework_parent_collection_uses_server_lesson_context(monkeypatch):
    calls = []
    async def authorize(_principal, student_id, group_id):
        calls.append((student_id, group_id))
    async def lesson_authorize(_principal, student_id, group_id, lesson_id):
        if lesson_id == 2:
            raise HTTPException(status_code=403, detail="wrong group")
        return {"group_id": group_id}
    class FakeService:
        def __init__(self, session): pass
        async def get_list(self, **_kwargs):
            return [SimpleNamespace(lesson_id=1), SimpleNamespace(lesson_id=2)], 2
    monkeypatch.setattr(homework_module, "require_parent_student_group", authorize)
    monkeypatch.setattr(homework_module, "require_parent_lesson_group", lesson_authorize)
    monkeypatch.setattr(homework_module, "HomeworkService", FakeService)
    monkeypatch.setattr(homework_module, "HomeworkListResponse", lambda **kwargs: kwargs)
    result = await homework_module.get_parent_child_group_homeworks_endpoint(20, 30, 0, 100, SimpleNamespace(), parent())
    assert calls == [(20, 30)]
    assert [row.lesson_id for row in result["items"]] == [1]


@pytest.mark.asyncio
async def test_submission_parent_collection_is_scoped_to_child_and_group(monkeypatch):
    async def authorize(_principal, student_id, group_id):
        assert (student_id, group_id) == (20, 30)
    async def lesson_authorize(*_args):
        return {"group_id": 30}
    class FakeService:
        def __init__(self, session): pass
        async def get_list(self, **kwargs):
            assert kwargs["student_id"] == 20 and kwargs["group_id"] == 30
            return [SimpleNamespace(homework_id=1)], 1
    class FakeSession:
        async def get(self, _model, _id):
            return SimpleNamespace(is_published=True, is_active=True, lesson_id=5)
    monkeypatch.setattr(submission_module, "require_parent_student_group", authorize)
    monkeypatch.setattr(submission_module, "require_parent_lesson_group", lesson_authorize)
    monkeypatch.setattr(submission_module, "HomeworkSubmissionService", FakeService)
    monkeypatch.setattr(submission_module, "HomeworkSubmissionListResponse", lambda **kwargs: kwargs)
    result = await submission_module.get_parent_child_group_submissions_endpoint(20, 30, 0, 100, FakeSession(), parent())
    assert len(result["items"]) == 1


def test_parent_content_mutations_are_not_role_allowed():
    source = Path("services/content_service/src/content_service/api/api_homework.py").read_text(encoding="utf-8")
    submission = Path("services/content_service/src/content_service/api/api_homework_submission.py").read_text(encoding="utf-8")
    assert "require_content_request" in source
    assert "require_content_request" in submission
    assert "RoleType.PARENT" not in source + submission