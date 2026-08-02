from pathlib import Path


def test_news_mutations_are_admin_and_author_is_principal():
    source = Path("services/news_service/src/news_service/api/api_post.py").read_text(encoding="utf-8")
    assert "Depends(require_admin())" in source
    assert "post_data.created_by = principal.user_id" in source


def test_public_news_forces_published_active_filter():
    source = Path("services/news_service/src/news_service/api/api_post.py").read_text(encoding="utf-8")
    assert "post_status = PostStatus.PUBLISHED" in source
    assert "is_active = True" in source
