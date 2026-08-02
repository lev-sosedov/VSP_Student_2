import importlib

import pytest


MODULES = [
    "auth_service.messaging.messaging_config",
    "user_service.messaging.messaging_config",
    "academic_service.messaging.messaging_config",
    "schedule_service.messaging.messaging_config",
    "content_service.messaging.messaging_config",
    "communication_service.messaging.messaging_config",
    "notification_service.messaging.messaging_config",
    "news_service.messaging.messaging_config",
]


def test_all_service_settings_expose_safe_common_contract(monkeypatch):
    monkeypatch.setenv("RABBITMQ_USERNAME", "contract-user")
    monkeypatch.setenv("RABBITMQ_PASSWORD", "contract-password")
    for name in MODULES:
        module = importlib.reload(importlib.import_module(name))
        settings = module.rabbitmq_settings
        assert settings.url.startswith("amqp://")
        assert settings.prefetch_count > 0
        assert settings.connection_timeout > 0
        assert "contract-password" not in repr(settings)


def test_legacy_environment_names_remain_compatible(monkeypatch):
    monkeypatch.setenv("RABBITMQ_USERNAME", "legacy-user")
    monkeypatch.setenv("RABBITMQ_PASSWORD", "legacy-password")
    monkeypatch.setenv("RABBITMQ_PREFETCH_COUNT", "7")
    module = importlib.reload(importlib.import_module("content_service.messaging.messaging_config"))
    assert module.rabbitmq_settings.prefetch_count == 7
    assert "legacy-password" not in repr(module.rabbitmq_settings)


def test_empty_connection_settings_fail_before_worker_start(monkeypatch):
    from common.rabbitmq_settings import RabbitMQSettingsMixin

    class Empty(RabbitMQSettingsMixin):
        host = ""
        username = ""
        password = ""

    with pytest.raises(ValueError, match="incomplete"):
        _ = Empty().url


def test_outbox_worker_and_startup_consumers_import_with_contract(monkeypatch):
    monkeypatch.setenv("RABBITMQ_USERNAME", "smoke-user")
    monkeypatch.setenv("RABBITMQ_PASSWORD", "smoke-password")
    from common.outbox_worker import OutboxWorker

    assert OutboxWorker
    for name in MODULES:
        module = importlib.reload(importlib.import_module(name))
        assert module.rabbitmq_settings.url
