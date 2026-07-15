import aio_pika
import asyncio

from academic_service.messaging.messaging_config import rabbitmq_settings


class RabbitConnection:
    _connection: aio_pika.RobustConnection | None = None
    _channel: aio_pika.RobustChannel | None = None

    # =====================================================
    # CONNECTION SINGLETON
    # =====================================================

    @classmethod
    async def connect(cls):

        if cls._connection and not cls._connection.is_closed:
            return cls._connection

        cls._connection = await aio_pika.connect_robust(
            host=rabbitmq_settings.host,
            port=rabbitmq_settings.port,
            login=rabbitmq_settings.username,
            password=rabbitmq_settings.password,
            virtualhost=rabbitmq_settings.virtual_host,
            heartbeat=rabbitmq_settings.heartbeat,
        )

        return cls._connection

    # =====================================================
    # CHANNEL SINGLETON
    # =====================================================

    @classmethod
    async def get_channel(cls):

        if cls._channel and not cls._channel.is_closed:
            return cls._channel

        connection = await cls.connect()

        cls._channel = await connection.channel()

        await cls._channel.set_qos(prefetch_count=rabbitmq_settings.prefetch_count)

        return cls._channel

    # =====================================================
    # CLOSE
    # =====================================================

    @classmethod
    async def close(cls):

        if cls._channel and not cls._channel.is_closed:
            await cls._channel.close()

        if cls._connection and not cls._connection.is_closed:
            await cls._connection.close()