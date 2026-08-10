import os
from types import SimpleNamespace

import pytest

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
os.environ.setdefault("RABBITMQ_USERNAME", "test")
os.environ.setdefault("RABBITMQ_PASSWORD", "test")

from schedule_service.messaging import messaging_rpc_server as rpc_module
from schedule_service.messaging.messaging_rpc_server import ScheduleRpcServer


class _Session:
    def __init__(self, lesson):
        self.lesson = lesson

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return False

    async def get(self, _model, _lesson_id):
        return self.lesson


@pytest.mark.asyncio
async def test_get_lesson_by_id_always_returns_dictionary(monkeypatch):
    lesson = SimpleNamespace(
        id=7,
        group_id=3,
        teacher_id=11,
        room_id=2,
        template_id=None,
        status="completed",
        lesson_type="lecture",
        is_extra=False,
        lesson_date=SimpleNamespace(isoformat=lambda: "2026-08-03"),
        start_time=SimpleNamespace(isoformat=lambda: "10:00:00"),
        end_time=SimpleNamespace(isoformat=lambda: "11:30:00"),
    )
    monkeypatch.setattr(rpc_module, "AsyncSessionLocal", lambda: _Session(lesson))

    response = await ScheduleRpcServer().get_lesson_by_id({"lesson_id": 7})

    assert isinstance(response, dict)
    assert response["success"] is True
    assert response["lesson"]["id"] == 7


@pytest.mark.asyncio
async def test_get_lesson_by_id_missing_and_invalid_are_dictionaries(monkeypatch):
    monkeypatch.setattr(rpc_module, "AsyncSessionLocal", lambda: _Session(None))
    server = ScheduleRpcServer()

    missing = await server.get_lesson_by_id({"lesson_id": 999})
    invalid = await server.get_lesson_by_id({"lesson_id": "not-an-id"})

    assert missing == {"success": True, "lesson": None}
    assert invalid["success"] is False


@pytest.mark.asyncio
async def test_lesson_context_remains_typed_dictionary(monkeypatch):
    lesson = SimpleNamespace(id=7, group_id=3, teacher_id=11, status="scheduled")
    monkeypatch.setattr(rpc_module, "AsyncSessionLocal", lambda: _Session(lesson))

    response = await ScheduleRpcServer().get_lesson_context({"lesson_id": 7})

    assert response == {
        "success": True,
        "exists": True,
        "lesson_id": 7,
        "group_id": 3,
        "teacher_id": 11,
        "status": "scheduled",
    }
