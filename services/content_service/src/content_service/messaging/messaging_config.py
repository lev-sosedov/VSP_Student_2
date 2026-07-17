import os


class RabbitMQSettings:
    host: str = os.getenv(
        "RABBITMQ_HOST",
        "rabbitmq"
    )

    port: int = int(
        os.getenv(
            "RABBITMQ_PORT",
            "5672"
        )
    )

    username: str = os.getenv(
        "RABBITMQ_USERNAME",
        "guest"
    )

    password: str = os.getenv(
        "RABBITMQ_PASSWORD",
        "guest"
    )

    virtual_host: str = os.getenv(
        "RABBITMQ_VIRTUAL_HOST",
        "/"
    )

    heartbeat: int = int(
        os.getenv(
            "RABBITMQ_HEARTBEAT",
            "60"
        )
    )

    prefetch_count: int = int(
        os.getenv(
            "RABBITMQ_PREFETCH_COUNT",
            "10"
        )
    )

    reconnect_interval: int = int(
        os.getenv(
            "RABBITMQ_RECONNECT_INTERVAL",
            "5"
        )
    )

    schedule_rpc_queue: str = os.getenv(
        "SCHEDULE_RPC_QUEUE",
        "schedule_service.rpc"
    )

    academic_rpc_queue: str = os.getenv(
        "ACADEMIC_RPC_QUEUE",
        "academic_service.rpc"
    )

    user_rpc_queue: str = os.getenv(
        "USER_RPC_QUEUE",
        "user_service.rpc"
    )

    exchange: str = os.getenv(
        "RABBITMQ_EXCHANGE",
        "vsh_student"
    )

    exchange_type: str = os.getenv(
        "RABBITMQ_EXCHANGE_TYPE",
        "topic"
    )

    durable: bool = (
            os.getenv(
                "RABBITMQ_DURABLE",
                "true"
            ).lower()
            == "true"
    )

    mandatory: bool = (
            os.getenv(
                "RABBITMQ_MANDATORY",
                "false"
            ).lower()
            == "true"
    )

    persistent_messages: bool = (
            os.getenv(
                "RABBITMQ_PERSISTENT_MESSAGES",
                "true"
            ).lower()
            == "true"
    )


rabbitmq_settings = RabbitMQSettings()