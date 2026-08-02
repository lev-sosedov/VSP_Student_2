from pathlib import Path


def test_schedule_lesson_context_contract_is_declared():
    source = Path("services/schedule_service/src/schedule_service/messaging/messaging_rpc_server.py").read_text(encoding="utf-8")
    assert "schedule.authorization.lesson_context" in source
    for field in ("exists", "lesson_id", "group_id", "teacher_id", "status"):
        assert f'"{field}"' in source


def test_content_routers_use_fail_closed_resource_guard():
    root = Path("services/content_service/src/content_service/api")
    for name in ("api_homework.py", "api_homework_submission.py", "api_lesson_content.py", "api_lesson_link.py", "api_lesson_attachment.py", "api_homework_attachment.py", "api_submission_attachment.py"):
        source = (root / name).read_text(encoding="utf-8")
        assert "require_content_request" in source


def test_submission_identity_and_lesson_membership_are_checked():
    source = (Path("services/content_service/src/content_service/api/api_homework_submission.py")).read_text(encoding="utf-8")
    assert "Cannot submit as another student" in source
    assert "require_lesson_role" in source


def test_attachment_owner_fields_are_not_trusted():
    source = (Path("services/content_service/src/content_service/api/api_submission_attachment.py")).read_text(encoding="utf-8")
    assert "uploaded_by must match authenticated user" in source
    assert "deleted_by" in source


def test_collections_filter_by_principal_groups_without_resource_context():
    auth = Path("services/content_service/src/content_service/api/authorization.py").read_text(encoding="utf-8")
    homework = Path("services/content_service/src/content_service/api/api_homework.py").read_text(encoding="utf-8")
    contents = Path("services/content_service/src/content_service/api/api_lesson_content.py").read_text(encoding="utf-8")
    submissions = Path("services/content_service/src/content_service/api/api_homework_submission.py").read_text(encoding="utf-8")
    assert "academic.authorization.user_groups" in auth
    assert "filter_lesson_collection" in homework and "filter_lesson_collection" in contents
    assert "filter_submission_collection" in submissions
    assert "Resource context is required" not in auth
