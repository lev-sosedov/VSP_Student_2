from pathlib import Path


SOURCE = (
    Path(__file__).parents[1]
    / "src/user_service/api/api_parent_students.py"
).read_text(encoding="utf-8")


def test_parent_link_mutations_are_admin_only():
    assert SOURCE.count("Depends(require_admin())") >= 4


def test_parent_reads_use_principal_and_link_ownership():
    assert "Depends(get_current_principal)" in SOURCE
    assert "link.parent_id" in SOURCE
    assert "link.student_id" in SOURCE
    assert "parent_id != principal.user_id" in SOURCE
