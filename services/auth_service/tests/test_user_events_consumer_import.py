import os


def test_user_events_consumer_imports_with_configured_session_factory():
    os.environ.setdefault("JWT_PRIVATE_KEY_PATH", "../VSP_Student_2_jwt_private_key.pem")
    os.environ.setdefault("JWT_PUBLIC_KEY_PATH", "../VSP_Student_2_jwt_public_key.pem")
    from auth_service.db.db_session import async_session
    from auth_service.messaging.messaging_user_events import consume_user_events_forever

    assert callable(consume_user_events_forever)
    assert async_session is not None
