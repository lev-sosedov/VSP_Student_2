"""Versioned contracts shared by RabbitMQ publishers and consumers.

The module intentionally contains no service imports.  It is safe to use from
startup code, migration tests and workers alike.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, ValidationError


USER_EVENTS_EXCHANGE = "user_security_events"
USER_EVENTS_EXCHANGE_TYPE = "fanout"
AUTH_USER_SYNC_QUEUE = "auth_user_sync"
USER_EVENTS_ROUTING_KEY = ""

SUPPORTED_EVENT_VERSIONS = frozenset({1})


class EventEnvelope(BaseModel):
    """Stable domain-event envelope; RPC messages are deliberately separate."""

    model_config = ConfigDict(extra="forbid")

    event_id: UUID
    event_type: str = Field(min_length=1, max_length=128)
    event_version: int = Field(ge=1)
    occurred_at: datetime
    producer: str = Field(min_length=1, max_length=128)
    correlation_id: UUID | None = None
    causation_id: UUID | None = None
    payload: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create(
        cls,
        *,
        event_type: str,
        producer: str,
        payload: Mapping[str, Any] | None = None,
        event_version: int = 1,
        correlation_id: UUID | None = None,
        causation_id: UUID | None = None,
    ) -> "EventEnvelope":
        return cls(
            event_id=uuid4(),
            event_type=event_type,
            event_version=event_version,
            occurred_at=datetime.now(timezone.utc),
            producer=producer,
            correlation_id=correlation_id,
            causation_id=causation_id,
            payload=dict(payload or {}),
        )

    def validate_supported_version(self) -> "EventEnvelope":
        if self.event_version not in SUPPORTED_EVENT_VERSIONS:
            raise UnsupportedEventVersion(self.event_version)
        return self


class EventContractError(ValueError):
    """Malformed or unsupported event data; callers should dead-letter it."""


class UnsupportedEventVersion(EventContractError):
    def __init__(self, version: int):
        super().__init__(f"unsupported event version: {version}")
        self.version = version


def parse_event_envelope(body: bytes | str) -> EventEnvelope:
    """Parse and validate an event without ever logging its payload."""

    try:
        raw = body.decode("utf-8") if isinstance(body, bytes) else body
        return EventEnvelope.model_validate_json(raw).validate_supported_version()
    except (UnicodeDecodeError, ValidationError, ValueError) as exc:
        raise EventContractError("malformed event envelope") from exc
