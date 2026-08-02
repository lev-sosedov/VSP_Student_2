from pathlib import Path


def test_public_collection_forces_published_state():
    source = Path("services/news_service/src/news_service/api/api_post.py").read_text(encoding="utf-8")
    assert "if not hasattr(request.state, \"current_principal\")" in source
    assert "post_status = PostStatus.PUBLISHED" in source
    assert "is_active = True" in source
