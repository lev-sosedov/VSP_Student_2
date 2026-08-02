"""Immutable news_service schema baseline."""
from alembic import op
import sqlalchemy as sa

class _EnumType(sa.types.UserDefinedType):
    cache_ok = True
    def __init__(self, name): self.name = name
    def get_col_spec(self, **kwargs): return self.name

revision = "20260802_00"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute("DO $$ BEGIN CREATE TYPE post_type_enum AS ENUM ('post', 'important', 'event', 'achievement', 'article'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE post_status_enum AS ENUM ('draft', 'published', 'archived'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE post_comment_status_enum AS ENUM ('published', 'hidden', 'deleted'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE post_media_type_enum AS ENUM ('image', 'video', 'audio', 'document', 'link'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;")
    op.create_table(
        'posts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('post_type', _EnumType("post_type_enum"), nullable=False),
        sa.Column('status', _EnumType("post_status_enum"), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('slug', sa.String(length=600), nullable=False),
        sa.Column('summary', sa.String(length=1500)),
        sa.Column('content', sa.Text()),
        sa.Column('category', sa.String(length=100)),
        sa.Column('cover_media_url', sa.String(length=3000)),
        sa.Column('cover_media_type', sa.String(length=50)),
        sa.Column('cover_preview_url', sa.String(length=3000)),
        sa.Column('cover_width', sa.Integer()),
        sa.Column('cover_height', sa.Integer()),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_by', sa.Integer()),
        sa.Column('published_by', sa.Integer()),
        sa.Column('is_pinned', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('allow_comments', sa.Boolean(), nullable=False),
        sa.Column('send_notification', sa.Boolean(), nullable=False),
        sa.Column('views_count', sa.Integer(), nullable=False),
        sa.Column('comments_count', sa.Integer(), nullable=False),
        sa.Column('published_at', sa.DateTime()),
        sa.Column('expires_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_table(
        'post_comments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('post_id', sa.Integer(), sa.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('parent_comment_id', sa.Integer(), sa.ForeignKey('post_comments.id', ondelete='CASCADE')),
        sa.Column('text', sa.Text()),
        sa.Column('status', _EnumType("post_comment_status_enum"), nullable=False),
        sa.Column('is_edited', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('edited_at', sa.DateTime()),
        sa.Column('deleted_at', sa.DateTime()),
    )
    op.create_table(
        'post_media',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('post_id', sa.Integer(), sa.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('media_type', _EnumType("post_media_type_enum"), nullable=False),
        sa.Column('file_url', sa.String(length=3000), nullable=False),
        sa.Column('preview_url', sa.String(length=3000)),
        sa.Column('file_name', sa.String(length=255)),
        sa.Column('mime_type', sa.String(length=150)),
        sa.Column('file_size', sa.Integer()),
        sa.Column('width', sa.Integer()),
        sa.Column('height', sa.Integer()),
        sa.Column('duration_seconds', sa.Integer()),
        sa.Column('alt_text', sa.String(length=500)),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_table(
        'post_views',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('post_id', sa.Integer(), sa.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('viewed_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('post_id', 'user_id', name='uq_post_view_post_user'),
    )
    op.create_index('ix_posts_created_at', 'posts', ['created_at'], unique=False)
    op.create_index('ix_posts_id', 'posts', ['id'], unique=False)
    op.create_index('ix_posts_created_by', 'posts', ['created_by'], unique=False)
    op.create_index('ix_posts_slug', 'posts', ['slug'], unique=True)
    op.create_index('ix_posts_category', 'posts', ['category'], unique=False)
    op.create_index('ix_posts_published_at', 'posts', ['published_at'], unique=False)
    op.create_index('ix_posts_is_pinned', 'posts', ['is_pinned'], unique=False)
    op.create_index('ix_posts_status', 'posts', ['status'], unique=False)
    op.create_index('ix_posts_expires_at', 'posts', ['expires_at'], unique=False)
    op.create_index('ix_posts_is_active', 'posts', ['is_active'], unique=False)
    op.create_index('ix_posts_post_type', 'posts', ['post_type'], unique=False)
    op.create_index('ix_post_comments_author_id', 'post_comments', ['author_id'], unique=False)
    op.create_index('ix_post_comments_id', 'post_comments', ['id'], unique=False)
    op.create_index('ix_post_comments_status', 'post_comments', ['status'], unique=False)
    op.create_index('ix_post_comments_post_id', 'post_comments', ['post_id'], unique=False)
    op.create_index('ix_post_comments_created_at', 'post_comments', ['created_at'], unique=False)
    op.create_index('ix_post_comments_parent_comment_id', 'post_comments', ['parent_comment_id'], unique=False)
    op.create_index('ix_post_media_post_id', 'post_media', ['post_id'], unique=False)
    op.create_index('ix_post_media_media_type', 'post_media', ['media_type'], unique=False)
    op.create_index('ix_post_media_id', 'post_media', ['id'], unique=False)
    op.create_index('ix_post_media_uploaded_by', 'post_media', ['uploaded_by'], unique=False)
    op.create_index('ix_post_views_id', 'post_views', ['id'], unique=False)
    op.create_index('ix_post_views_post_id', 'post_views', ['post_id'], unique=False)
    op.create_index('ix_post_views_user_id', 'post_views', ['user_id'], unique=False)

def downgrade() -> None:
    # Baseline downgrades are intentionally non-destructive.
    pass
