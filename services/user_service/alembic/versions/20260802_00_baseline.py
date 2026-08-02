"""Immutable user_service schema baseline."""
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
    op.execute("DO $$ BEGIN CREATE TYPE roletype AS ENUM ('USER', 'PARENT', 'STUDENT', 'TEACHER', 'ADMIN'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;")
    op.create_table(
        'user_event_outbox',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('event_id', sa.String(length=64), nullable=False),
        sa.Column('event_type', sa.String(length=64), nullable=False),
        sa.Column('event_version', sa.Integer(), nullable=False),
        sa.Column('occurred_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('auth_id', sa.Integer()),
        sa.Column('payload', sa.Text(), nullable=False),
        sa.Column('published_at', sa.DateTime()),
        sa.UniqueConstraint('event_id', name='uq_user_event_outbox_event_id'),
    )
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('auth_id', sa.Integer()),
        sa.Column('phone_number', sa.String(length=20), nullable=False),
        sa.Column('user_name', sa.String(length=50)),
        sa.Column('role', _EnumType("roletype"), nullable=False),
        sa.Column('email', sa.String(length=255)),
        sa.Column('first_name', sa.String(length=100)),
        sa.Column('last_name', sa.String(length=100)),
        sa.Column('birthday', sa.Date()),
        sa.Column('avatar_url', sa.String(length=500)),
        sa.Column('about', sa.String(length=1000)),
        sa.Column('is_active', sa.Boolean()),
        sa.Column('is_account_verified', sa.Boolean()),
        sa.Column('is_phone_verified', sa.Boolean()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.UniqueConstraint('phone_number'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('auth_id'),
    )
    op.create_table(
        'parent_student_links',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('parent_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('student_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('relationship', sa.String(length=30), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.UniqueConstraint('parent_id', 'student_id', name='uq_parent_student_link'),
    )
    op.create_index('ix_parent_student_links_student_id', 'parent_student_links', ['student_id'], unique=False)
    op.create_index('ix_parent_student_links_id', 'parent_student_links', ['id'], unique=False)
    op.create_index('ix_parent_student_links_parent_id', 'parent_student_links', ['parent_id'], unique=False)
    op.create_index('ix_user_event_outbox_user_id', 'user_event_outbox', ['user_id'], unique=False)

def downgrade() -> None:
    # Baseline downgrades are intentionally non-destructive.
    pass
