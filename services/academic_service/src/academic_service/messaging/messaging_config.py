from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)
from common.rabbitmq_settings import RabbitMQSettingsMixin


class RabbitMQSettings(RabbitMQSettingsMixin, BaseSettings):
    host: str = "rabbitmq"
    port: int = 5672

    username: str
    password: str

    virtual_host: str = "/"

    exchange: str = "vsh_student"
    exchange_type: str = "topic"

    queue: str = "academic_service"
    routing_key: str = "academic.#"

    # Очередь, которую слушает RPC-сервер
    # academic-service
    academic_rpc_queue: str = "academic_service.rpc"

    # Очередь, куда academic-service отправляет
    # RPC-запросы в user-service
    user_rpc_queue: str = "user_service.rpc"

    prefetch_count: int = 10
    reconnect_interval: int = 5
    heartbeat: int = 60
    connection_timeout_seconds: float = 10.0

    durable: bool = True
    mandatory: bool = False
    persistent_messages: bool = True

    model_config = SettingsConfigDict(
        env_prefix="RABBITMQ_",
        extra="ignore"
    )

rabbitmq_settings = RabbitMQSettings()


# =====================================================
# Aliases
# =====================================================

ACADEMIC_QUEUE = rabbitmq_settings.queue

ACADEMIC_ROUTING_KEYS = [
    rabbitmq_settings.routing_key
]
