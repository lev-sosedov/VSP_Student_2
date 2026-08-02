from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_backend_workflow_has_safe_triggers_and_jobs():
    workflow = (ROOT / ".github" / "workflows" / "backend-ci.yml").read_text(encoding="utf-8")
    assert "pull_request:" in workflow
    assert "workflow_dispatch:" in workflow
    assert "configuration-and-quality:" in workflow
    assert "tests:" in workflow
    assert "alembic:" in workflow
    assert "docker-build:" in workflow
    assert "docker push" not in workflow
    assert "docker compose down" not in workflow


def test_ci_does_not_reference_production_secrets_or_database():
    workflow = (ROOT / ".github" / "workflows" / "backend-ci.yml").read_text(encoding="utf-8")
    forbidden = ("JWT_SECRET_KEY", "PROD_DATABASE", "VSP_Student_2_database_backup", "docker volume rm")
    assert not any(value in workflow for value in forbidden)
