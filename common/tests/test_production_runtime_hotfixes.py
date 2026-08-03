import importlib
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from common.rabbitmq_settings import RabbitMQSettingsMixin
from common.security.middleware import JWTAuthenticationMiddleware


class Settings(RabbitMQSettingsMixin):
    host = "rabbitmq"
    port = 5672
    username = "user@example"
    password = "p@ss word/with?chars"
    virtual_host = "/"


def test_root_vhost_and_credentials_are_percent_encoded():
    url = Settings().url
    assert url == (
        "amqp://user%40example:p%40ss%20word%2Fwith%3Fchars@rabbitmq:5672/%2F"
    )


def test_production_rabbit_consumers_do_not_use_guest_credentials():
    root = Path(__file__).parents[2]
    files = (
        root / "services/auth_service/src/auth_service/messaging/messaging_rabbit.py",
        root / "services/user_service/src/user_service/messaging/messaging_rabbit.py",
    )
    assert all("guest:guest" not in path.read_text(encoding="utf-8") for path in files)


def test_service_public_paths_are_exactly_configured(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
    monkeypatch.setenv("RABBITMQ_USERNAME", "test")
    monkeypatch.setenv("RABBITMQ_PASSWORD", "test")

    user_app = importlib.import_module("user_service.main").app
    academic_app = importlib.import_module("academic_service.main").app
    user_paths = user_app.user_middleware[0].kwargs["public_paths"]
    academic_paths = academic_app.user_middleware[0].kwargs["public_paths"]
    assert user_paths == {"/api/v1/users/public/teachers"}
    assert academic_paths == {"/api/v1/branches"}


def test_public_routes_pass_and_other_routes_require_jwt():
    app = FastAPI()
    app.add_middleware(
        JWTAuthenticationMiddleware,
        public_paths={"/api/v1/users/public/teachers", "/api/v1/branches"},
    )

    @app.get("/api/v1/users/public/teachers")
    async def public_teachers():
        return {"ok": True}

    @app.get("/api/v1/branches")
    async def public_branches():
        return {"ok": True}

    @app.get("/api/v1/users")
    async def protected_users():
        return {"ok": True}

    @app.get("/api/v1/branch-private")
    async def protected_branch():
        return {"ok": True}

    client = TestClient(app)
    assert client.get("/api/v1/users/public/teachers").status_code == 200
    assert client.get("/api/v1/branches").status_code == 200
    assert client.get("/api/v1/users").status_code == 401
    assert client.get("/api/v1/branch-private").status_code == 401
