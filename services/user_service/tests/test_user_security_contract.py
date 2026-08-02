from pathlib import Path


API = Path(__file__).parents[1] / "src/user_service/api/api_users.py"
SOURCE = API.read_text(encoding="utf-8")


def test_self_profile_routes_use_principal_contract():
    assert '@router.get("/me"' in SOURCE
    assert '@router.patch("/me"' in SOURCE
    assert "principal.user_id" in SOURCE


def test_delete_is_admin_only_and_public_teacher_is_separate():
    delete_block = SOURCE.split('@router.delete(', 1)[1]
    assert "require_admin()" in delete_block
    assert '@router.get(\n    "/public/teachers"' in SOURCE
