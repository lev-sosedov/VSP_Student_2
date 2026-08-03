"""Shared, non-secret RabbitMQ settings contract used by every service."""

from urllib.parse import quote


class RabbitMQSettingsMixin:
    """Compatibility properties for legacy service-specific settings classes."""

    @property
    def url(self) -> str:
        host = str(getattr(self, "host", "")).strip()
        username = str(getattr(self, "username", "")).strip()
        password = str(getattr(self, "password", ""))
        if not host or not username or not password:
            raise ValueError("RabbitMQ connection settings are incomplete")
        port = int(getattr(self, "port", 5672))
        virtual_host = str(getattr(self, "virtual_host", "/")) or "/"
        return (
            f"amqp://{quote(username, safe='')}:{quote(password, safe='')}"
            f"@{host}:{port}/{quote(virtual_host, safe='')}"
        )

    @property
    def connection_timeout(self) -> float:
        return float(getattr(self, "connection_timeout_seconds", 10.0))

    @property
    def retry_max_attempts(self) -> int:
        return int(getattr(self, "max_retry_attempts", 3))

    @property
    def retry_base_delay_seconds(self) -> float:
        return float(getattr(self, "retry_interval", 5.0))

    def __repr__(self) -> str:
        return f"{type(self).__name__}(host={getattr(self, 'host', '')!r}, port={getattr(self, 'port', '')!r})"
