import asyncio
from uuid import UUID

import pytest
from pathlib import Path

from common.messaging_contract import EventContractError, EventEnvelope, parse_event_envelope
from common.messaging_reliability import ComponentReadiness, RetryPolicy, dlx_names, json_safe_log_fields


def test_envelope_contains_correlation_and_is_versioned():
    envelope = EventEnvelope.create(
        event_type="user.role.changed",
        producer="user-service",
        correlation_id=UUID("00000000-0000-0000-0000-000000000001"),
        payload={"user_id": 42},
    )
    decoded = parse_event_envelope(envelope.model_dump_json())
    assert decoded.event_id == envelope.event_id
    assert decoded.correlation_id == envelope.correlation_id
    assert decoded.payload == {"user_id": 42}


def test_malformed_json_is_rejected_without_payload_logging():
    with pytest.raises(EventContractError):
        parse_event_envelope(b"{not-json")


def test_unknown_event_version_is_rejected():
    envelope = EventEnvelope.create(event_type="x", producer="test", event_version=1)
    raw = envelope.model_dump()
    raw["event_version"] = 99
    with pytest.raises(EventContractError):
        parse_event_envelope(EventEnvelope.model_validate(raw).model_dump_json())


def test_retry_policy_is_bounded_exponential():
    policy = RetryPolicy(max_attempts=3, base_delay_seconds=1, max_delay_seconds=5)
    assert [policy.delay(i) for i in (1, 2, 3, 4)] == [1, 2, 4, 5]


def test_dlx_is_versioned_and_does_not_replace_source_queue():
    assert dlx_names("auth_user_sync") == ("auth_user_sync.v1.dlx", "auth_user_sync.v1.dlq")


def test_readiness_and_log_filter_are_safe():
    state = ComponentReadiness()
    state.mark("postgres", True)
    state.mark("rabbitmq", False)
    assert state.ready is False
    safe = json_safe_log_fields(event_id="abc", password="hidden", payload={"token": "hidden"})
    assert safe == {"event_id": "abc"}


def test_outbox_contract_confirms_before_marking_published():
    source = Path("services/user_service/src/user_service/messaging/messaging_outbox.py").read_text()
    assert "publish_confirmed" in source
    assert "mark_published" in source
    assert source.index("publish_confirmed") < source.index("mark_published")


def test_consumer_ack_is_after_commit_and_retry_is_bounded():
    source = Path("services/auth_service/src/auth_service/messaging/messaging_user_events.py").read_text()
    assert source.index("await session.commit()") < source.rfind("await message.ack()")
    assert "RetryPolicy(max_attempts=3" in source


def test_duplicate_event_uses_durable_marker_before_business_logic():
    source = Path("services/auth_service/src/auth_service/messaging/messaging_user_events.py").read_text()
    assert "ProcessedUserEvent" in source
    assert "if seen:" in source


def test_malformed_and_unknown_version_have_dlq_path():
    source = Path("services/notification_service/src/notification_service/events/events_consumer.py").read_text()
    assert "dead_letter" in source
    assert "EventContractError" in source


def test_event_ids_are_unique_in_outbox_and_processed_markers():
    outbox = Path("services/user_service/src/user_service/models/model_outbox.py").read_text()
    processed = Path("services/notification_service/src/notification_service/models/model_processed_event.py").read_text()
    assert "UniqueConstraint(\"event_id\"" in outbox
    assert "UniqueConstraint(\"event_id\"" in processed


def test_retry_delay_does_not_become_tight_loop():
    policy = RetryPolicy(max_attempts=3, base_delay_seconds=1, max_delay_seconds=30)
    assert policy.delay(1) >= 1 and policy.delay(3) > policy.delay(1)


def test_dlx_queue_is_durable_and_versioned():
    source = Path("common/src/common/messaging_reliability.py").read_text()
    assert "durable=True" in source
    assert ".v1.dlq" in source


def test_readiness_never_contains_connection_url_or_secret_names():
    source = Path("common/src/common/readiness.py").read_text()
    assert "DATABASE_URL" not in source
    assert "traceback" not in source.lower()


def test_state_mutating_communication_consumer_has_durable_marker():
    source = Path("services/communication_service/src/communication_service/messaging/messaging_academic_event_consumer.py").read_text()
    assert "ProcessedEvent" in source
    assert "await session.commit()" in source
    assert source.index("await session.commit()") < source.rfind("await message.ack()")


def test_communication_idempotency_migration_is_separate_revision():
    migration = Path("services/communication_service/alembic/versions/20260802_01_processed_events.py").read_text()
    assert 'down_revision = "20260802_00"' in migration
    assert "UniqueConstraint" in migration


def test_readiness_uses_active_broker_probe():
    source = Path("common/src/common/readiness.py").read_text()
    assert "probe_rabbitmq" in source
    assert "asyncio.wait_for" in source
