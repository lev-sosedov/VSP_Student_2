from auth_service.repositories.repository_refresh_session import hash_refresh_token


def test_refresh_tokens_are_stored_as_one_way_hashes():
    token = "opaque-refresh-token"
    digest = hash_refresh_token(token)
    assert digest != token
    assert len(digest) == 64
    assert digest == hash_refresh_token(token)
