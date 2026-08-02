"""Request-local SQLAlchemy session context for transactional event enqueueing."""
from contextvars import ContextVar
from typing import Any

current_session: ContextVar[Any | None] = ContextVar("current_outbox_session", default=None)


def bind_session(session: Any):
    return current_session.set(session)


def unbind_session(token) -> None:
    current_session.reset(token)
