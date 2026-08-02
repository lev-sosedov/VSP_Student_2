from pydantic_settings import BaseSettings, SettingsConfigDict
from common.rabbitmq_settings import RabbitMQSettingsMixin


class RabbitMQSettings(RabbitMQSettingsMixin, BaseSettings):
    host: str = "rabbitmq"
    port: int = 5672

    username: str
    password: str

    virtual_host: str = "/"

    rpc_queue: str = "user_service.rpc"

    prefetch_count: int = 10
    reconnect_interval: int = 5
    heartbeat: int = 60

    environment: str = "development"

    model_config = SettingsConfigDict(
        env_prefix="RABBITMQ_",
        extra="ignore"
    )

rabbitmq_settings = RabbitMQSettings()
