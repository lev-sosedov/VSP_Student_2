import aio_pika

from news_service.messaging.messaging_config import (
    rabbitmq_settings
)


class RabbitConnection:
    _connection: aio_pika.RobustConnection | None = None
    _channel: aio_pika.RobustChannel | None = None

    # =================================================
    # CONNECT
    # =================================================

    @classmethod
    async def connect(
        cls
    ) -> aio_pika.RobustConnection:
        if (
            cls._connection is not None
            and not cls._connection.is_closed
        ):
            return cls._connection

        cls._connection = await aio_pika.connect_robust(
            host=rabbitmq_settings.host,
            port=rabbitmq_settings.port,
            login=rabbitmq_settings.username,
            password=rabbitmq_settings.password,
            virtualhost=rabbitmq_settings.virtual_host,
            heartbeat=rabbitmq_settings.heartbeat
        )

        return cls._connection

    # =================================================
    # CHANNEL
    # =================================================

    @classmethod
    async def get_channel(
        cls
    ) -> aio_pika.RobustChannel:
        if (
            cls._channel is not None
            and not cls._channel.is_closed
        ):
            return cls._channel

        connection = await cls.connect()

        cls._channel = await connection.channel()

        await cls._channel.set_qos(
            prefetch_count=(
                rabbitmq_settings.prefetch_count
            )
        )

        return cls._channel

    # =================================================
    # CLOSE
    # =================================================

    @classmethod
    async def close(cls) -> None:
        if (
            cls._channel is not None
            and not cls._channel.is_closed
        ):
            await cls._channel.close()

        if (
            cls._connection is not None
            and not cls._connection.is_closed
        ):
            await cls._connection.close()

        cls._channel = None
        cls._connection = None