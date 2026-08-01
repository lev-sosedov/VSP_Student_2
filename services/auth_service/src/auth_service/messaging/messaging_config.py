from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RabbitMQSettings(BaseSettings):
    host: str = "rabbitmq"
    port: int = Field(default=5672, gt=0, le=65535)
    username: str
    password: str
    virtual_host: str = "/"
    user_rpc_queue: str = "user_service.rpc"
    rpc_timeout_seconds: float = Field(default=5.0, gt=0)
    heartbeat: int = 60

    model_config = SettingsConfigDict(env_prefix="RABBITMQ_", extra="ignore")

    @property
    def url(self) -> str:
        return (
            f"amqp://{self.username}:{self.password}@"
            f"{self.host}:{self.port}/{self.virtual_host.lstrip('/')}"
        )


rabbitmq_settings = RabbitMQSettings()
