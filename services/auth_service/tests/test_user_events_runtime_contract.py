from pathlib import Path

from common.messaging_contract import AUTH_USER_SYNC_QUEUE, USER_EVENTS_EXCHANGE, USER_EVENTS_ROUTING_KEY


def test_user_event_contract_matches_publisher_and_consumer():
    auth = Path("services/auth_service/src/auth_service/messaging/messaging_user_events.py").read_text()
    publisher = Path("services/user_service/src/user_service/messaging/messaging_outbox.py").read_text()
    assert "USER_EVENTS_EXCHANGE" in auth and "USER_EVENTS_EXCHANGE" in publisher
    assert "AUTH_USER_SYNC_QUEUE" in auth
    assert USER_EVENTS_ROUTING_KEY == ""
    assert "durable=True" in auth
    assert "exclusive=False" in auth
    assert "auto_delete=False" in auth
    assert "await message.ack()" in auth
    assert "retry_or_dead_letter" in auth
    assert "dead_letter" in auth
    assert "await session.commit()" in auth


def test_activation_event_restores_auth_state_and_rotates_version():
    auth = Path("services/auth_service/src/auth_service/messaging/messaging_user_events.py").read_text()
    user = Path("services/user_service/src/user_service/services/service_user.py").read_text()
    assert 'event_type == "user.activated"' in auth
    assert '"user.activated"' in user
    assert 'user.is_active = True' in auth
    assert 'event_type in {"user.role.changed", "user.blocked", "user.deleted", "user.activated", "user.password.changed"}' in auth
