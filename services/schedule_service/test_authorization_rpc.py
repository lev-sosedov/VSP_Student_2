from pathlib import Path


def test_schedule_group_listing_uses_academic_membership_rpc():
    source = Path("services/schedule_service/src/schedule_service/api/authorization.py").read_text(encoding="utf-8")
    route = Path("services/schedule_service/src/schedule_service/api/api_lesson_schedule.py").read_text(encoding="utf-8")
    assert "academic.authorization.membership" in source
    assert "timeout=2.0" in source
    assert "require_group_member_or_admin" in route


def test_attendance_routes_use_resource_dependencies():
    source = Path("services/schedule_service/src/schedule_service/api/api_attendance.py").read_text(encoding="utf-8")
    assert "require_lesson_teacher_or_admin" in source
    assert "require_student_self_or_admin" in source
    assert "require_attendance_access" in source
    assert "require_attendance_teacher_or_admin" in source
    assert "academic.authorization.membership" in source


def test_all_lesson_mutations_and_reads_are_resource_protected():
    route = Path("services/schedule_service/src/schedule_service/api/api_lesson_schedule.py").read_text(encoding="utf-8")
    assert "require_lesson_access" in route
    assert route.count("require_lesson_teacher_or_admin") >= 4
    assert "require_group_member_or_admin" in route
    assert "Teacher identity mismatch" in route


def test_global_attendance_listing_is_not_public():
    route = Path("services/schedule_service/src/schedule_service/api/api_attendance.py").read_text(encoding="utf-8")
    assert "Global attendance list is restricted" in route
    assert "require_attendance_teacher_or_admin" in route
    assert "require_student_self_or_admin" in route
