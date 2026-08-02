from pathlib import Path


def test_chat_member_dependency_checks_academic_membership_fail_closed():
    source = Path("services/communication_service/src/communication_service/api/dependencies.py").read_text(encoding="utf-8")
    assert "academic.authorization.membership" in source
    assert "Academic group authorization unavailable" in source


def test_group_chat_creation_requires_teacher_or_admin():
    source = Path("services/communication_service/src/communication_service/api/api_chat.py").read_text(encoding="utf-8")
    assert "Only teachers or administrators may create group chats" in source
    assert "created_by must match authenticated user" in source


def test_private_pair_schema_is_canonical_and_legacy_safe():
    model = Path("services/communication_service/src/communication_service/models/model_chat.py").read_text(encoding="utf-8")
    migration = Path("services/communication_service/migrations/20260802_01_private_chat_pair.sql").read_text(encoding="utf-8")
    assert "participant_one_id" in model and "participant_two_id" in model
    assert "uq_private_chat_canonical_pair" in migration
    assert "legacy rows remain" in migration


def test_websocket_and_http_require_active_member():
    http = Path("services/communication_service/src/communication_service/api/dependencies.py").read_text(encoding="utf-8")
    ws = Path("services/communication_service/src/communication_service/api/api_websocket.py").read_text(encoding="utf-8")
    assert "member.is_active" in http
    assert "validate_websocket_access" in ws
