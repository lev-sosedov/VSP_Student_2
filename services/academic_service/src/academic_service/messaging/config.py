from pydantic_settings import BaseSettings, SettingsConfigDict


class RabbitMQSettings(BaseSettings):

    host: str = "localhost"
    port: int = 5672
    username: str = "guest"
    password: str = "guest"
    virtual_host: str = "/"

    exchange: str = "vsh_student"
    exchange_type: str = "topic"

    queue: str = "academic_service"
    routing_key: str = "academic.#"

    durable: bool = True
    prefetch_count: int = 10
    reconnect_interval: int = 5
    heartbeat: int = 60

    mandatory: bool = False
    persistent_messages: bool = True

    model_config = SettingsConfigDict(
        env_prefix="RABBITMQ_",
        extra="ignore"
    )


rabbitmq_settings = RabbitMQSettings()

# aliases
ACADEMIC_QUEUE = rabbitmq_settings.queue
ACADEMIC_ROUTING_KEYS = [rabbitmq_settings.routing_key]