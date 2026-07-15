from pydantic_settings import BaseSettings, SettingsConfigDict


class RabbitMQSettings(BaseSettings):
    host: str = "rabbitmq"
    port: int = 5672

    username: str = "guest"
    password: str = "guest"

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

    @property
    def url(self) -> str:
        return (
            f"amqp://{self.username}:"
            f"{self.password}@"
            f"{self.host}:"
            f"{self.port}/"
        )


rabbitmq_settings = RabbitMQSettings()
