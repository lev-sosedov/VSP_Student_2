from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from common.rabbitmq_settings import RabbitMQSettingsMixin


class RabbitMQSettings(RabbitMQSettingsMixin, BaseSettings):
    host: str = "rabbitmq"
    port: int = Field(default=5672, gt=0, le=65535)
    username: str
    password: str
    virtual_host: str = "/"
    user_rpc_queue: str = "user_service.rpc"
    rpc_timeout_seconds: float = Field(default=5.0, gt=0)
    prefetch_count: int = Field(default=10, gt=0)
    connection_timeout_seconds: float = Field(default=10.0, gt=0)
    heartbeat: int = 60

    model_config = SettingsConfigDict(env_prefix="RABBITMQ_", extra="ignore")

rabbitmq_settings = RabbitMQSettings()
