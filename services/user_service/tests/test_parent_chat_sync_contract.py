from pathlib import Path


SOURCE = Path(
    "services/user_service/src/user_service/messaging/messaging_rpc_server.py"
).read_text(encoding="utf-8")


def test_parent_students_rpc_is_internal_and_returns_ids_only():
    assert '"parent.authorization.students"' in SOURCE
    assert "async def parent_students" in SOURCE
    assert '"student_ids"' in SOURCE
    assert "ParentStudentLink.parent_id" in SOURCE
    assert "User.is_active.is_(True)" in SOURCE


def test_parent_chat_sync_is_fail_closed_and_server_side():
    source = Path(
        "services/communication_service/src/communication_service/api/api_chat.py"
    ).read_text(encoding="utf-8")
    assert "parent.authorization.students" in source
    assert "academic.authorization.user_groups" in source
    assert "group_members.get_by_group" in source
    assert "Parent chat authorization unavailable" in source
    assert "ensure_private_chat" in source


def test_unread_count_is_self_or_admin_not_chat_member_route():
    source = Path(
        "services/communication_service/src/communication_service/api/api_message_read.py"
    ).read_text(encoding="utf-8")
    assert "Cannot query another user's unread count" in source
    assert "principal.user_id" in source


def test_private_chat_pair_is_canonical_and_idempotent():
    source = Path(
        "services/communication_service/src/communication_service/services/service_chat.py"
    ).read_text(encoding="utf-8")
    assert "sorted((first_user_id, second_user_id))" in source
    assert "pg_advisory_xact_lock" in source
    assert "except IntegrityError" in source
