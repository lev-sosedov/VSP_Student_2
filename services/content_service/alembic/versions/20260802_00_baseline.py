"""Immutable content_service schema baseline."""
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
    op.execute("DO $$ BEGIN CREATE TYPE attachment_type_enum AS ENUM ('DOCUMENT', 'PRESENTATION', 'IMAGE', 'VIDEO', 'AUDIO', 'ARCHIVE', 'CODE', 'OTHER'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE homework_submission_status_enum AS ENUM ('DRAFT', 'SUBMITTED', 'IN_REVIEW', 'NEEDS_REVISION', 'ACCEPTED', 'REJECTED'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;")
    op.create_table(
        'homeworks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('lesson_id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer()),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('instructions', sa.Text()),
        sa.Column('max_score', sa.Integer(), nullable=False),
        sa.Column('due_at', sa.DateTime()),
        sa.Column('allow_late_submission', sa.Boolean(), nullable=False),
        sa.Column('is_published', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_by', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('lesson_id', name='uq_homeworks_lesson_id'),
    )
    op.create_table(
        'lesson_contents',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('lesson_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('summary', sa.String(length=1000)),
        sa.Column('content', sa.Text()),
        sa.Column('is_published', sa.Boolean(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_by', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('lesson_id', name='uq_lesson_contents_lesson_id'),
    )
    op.create_table(
        'homework_attachments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('homework_id', sa.Integer(), sa.ForeignKey('homeworks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('attachment_type', _EnumType("attachment_type_enum"), nullable=False),
        sa.Column('file_url', sa.Text(), nullable=False),
        sa.Column('file_name', sa.String(length=255)),
        sa.Column('mime_type', sa.String(length=150)),
        sa.Column('file_size', sa.Integer()),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('is_visible', sa.Boolean(), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_table(
        'homework_submissions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('homework_id', sa.Integer(), sa.ForeignKey('homeworks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('answer_text', sa.Text()),
        sa.Column('status', _EnumType("homework_submission_status_enum"), nullable=False),
        sa.Column('score', sa.Integer()),
        sa.Column('teacher_comment', sa.Text()),
        sa.Column('checked_by', sa.Integer()),
        sa.Column('is_late', sa.Boolean(), nullable=False),
        sa.Column('submitted_at', sa.DateTime()),
        sa.Column('checked_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint('score IS NULL OR score >= 0', name='check_homework_submission_score_positive'),
        sa.UniqueConstraint('homework_id', 'student_id', name='uq_homework_submission_homework_student'),
    )
    op.create_table(
        'lesson_attachments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('lesson_content_id', sa.Integer(), sa.ForeignKey('lesson_contents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('attachment_type', _EnumType("attachment_type_enum"), nullable=False),
        sa.Column('file_url', sa.Text(), nullable=False),
        sa.Column('file_name', sa.String(length=255)),
        sa.Column('mime_type', sa.String(length=150)),
        sa.Column('file_size', sa.Integer()),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('is_visible', sa.Boolean(), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_table(
        'lesson_links',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('lesson_content_id', sa.Integer(), sa.ForeignKey('lesson_contents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('is_visible', sa.Boolean(), nullable=False),
        sa.Column('added_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_table(
        'submission_attachments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('submission_id', sa.Integer(), sa.ForeignKey('homework_submissions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('attachment_type', _EnumType("attachment_type_enum"), nullable=False),
        sa.Column('file_url', sa.Text(), nullable=False),
        sa.Column('file_name', sa.String(length=255)),
        sa.Column('mime_type', sa.String(length=150)),
        sa.Column('file_size', sa.Integer()),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_homeworks_id', 'homeworks', ['id'], unique=False)
    op.create_index('ix_homeworks_group_id', 'homeworks', ['group_id'], unique=False)
    op.create_index('ix_homeworks_updated_by', 'homeworks', ['updated_by'], unique=False)
    op.create_index('ix_homeworks_is_published', 'homeworks', ['is_published'], unique=False)
    op.create_index('ix_homeworks_created_by', 'homeworks', ['created_by'], unique=False)
    op.create_index('ix_homeworks_due_at', 'homeworks', ['due_at'], unique=False)
    op.create_index('ix_homeworks_is_active', 'homeworks', ['is_active'], unique=False)
    op.create_index('ix_homeworks_lesson_id', 'homeworks', ['lesson_id'], unique=False)
    op.create_index('ix_homework_attachments_attachment_type', 'homework_attachments', ['attachment_type'], unique=False)
    op.create_index('ix_homework_attachments_homework_id', 'homework_attachments', ['homework_id'], unique=False)
    op.create_index('ix_homework_attachments_uploaded_by', 'homework_attachments', ['uploaded_by'], unique=False)
    op.create_index('ix_homework_attachments_id', 'homework_attachments', ['id'], unique=False)
    op.create_index('ix_homework_attachments_is_visible', 'homework_attachments', ['is_visible'], unique=False)
    op.create_index('ix_homework_submissions_id', 'homework_submissions', ['id'], unique=False)
    op.create_index('ix_homework_submissions_submitted_at', 'homework_submissions', ['submitted_at'], unique=False)
    op.create_index('ix_homework_submissions_homework_id', 'homework_submissions', ['homework_id'], unique=False)
    op.create_index('ix_homework_submissions_student_id', 'homework_submissions', ['student_id'], unique=False)
    op.create_index('ix_homework_submissions_checked_by', 'homework_submissions', ['checked_by'], unique=False)
    op.create_index('ix_homework_submissions_status', 'homework_submissions', ['status'], unique=False)
    op.create_index('ix_homework_submissions_is_late', 'homework_submissions', ['is_late'], unique=False)
    op.create_index('ix_lesson_attachments_attachment_type', 'lesson_attachments', ['attachment_type'], unique=False)
    op.create_index('ix_lesson_attachments_uploaded_by', 'lesson_attachments', ['uploaded_by'], unique=False)
    op.create_index('ix_lesson_attachments_id', 'lesson_attachments', ['id'], unique=False)
    op.create_index('ix_lesson_attachments_is_visible', 'lesson_attachments', ['is_visible'], unique=False)
    op.create_index('ix_lesson_attachments_lesson_content_id', 'lesson_attachments', ['lesson_content_id'], unique=False)
    op.create_index('ix_lesson_contents_lesson_id', 'lesson_contents', ['lesson_id'], unique=True)
    op.create_index('ix_lesson_contents_created_by', 'lesson_contents', ['created_by'], unique=False)
    op.create_index('ix_lesson_contents_updated_by', 'lesson_contents', ['updated_by'], unique=False)
    op.create_index('ix_lesson_contents_is_published', 'lesson_contents', ['is_published'], unique=False)
    op.create_index('ix_lesson_contents_id', 'lesson_contents', ['id'], unique=False)
    op.create_index('ix_lesson_links_id', 'lesson_links', ['id'], unique=False)
    op.create_index('ix_lesson_links_is_visible', 'lesson_links', ['is_visible'], unique=False)
    op.create_index('ix_lesson_links_lesson_content_id', 'lesson_links', ['lesson_content_id'], unique=False)
    op.create_index('ix_lesson_links_added_by', 'lesson_links', ['added_by'], unique=False)
    op.create_index('ix_submission_attachments_uploaded_by', 'submission_attachments', ['uploaded_by'], unique=False)
    op.create_index('ix_submission_attachments_id', 'submission_attachments', ['id'], unique=False)
    op.create_index('ix_submission_attachments_attachment_type', 'submission_attachments', ['attachment_type'], unique=False)
    op.create_index('ix_submission_attachments_submission_id', 'submission_attachments', ['submission_id'], unique=False)

def downgrade() -> None:
    # Baseline downgrades are intentionally non-destructive.
    pass
