"""Immutable notification_service schema baseline."""
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
    op.execute("DO $$ BEGIN CREATE TYPE notification_type_enum AS ENUM ('SYSTEM', 'SCHEDULE', 'LESSON', 'HOMEWORK', 'HOMEWORK_RESULT', 'CHAT', 'MESSAGE', 'NEWS', 'COMMENT', 'USER', 'ACADEMIC'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE notification_priority_enum AS ENUM ('LOW', 'NORMAL', 'HIGH', 'URGENT'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE notification_channel_enum AS ENUM ('IN_APP', 'EMAIL', 'PUSH', 'TELEGRAM'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE notification_status_enum AS ENUM ('PENDING', 'DELIVERED', 'FAILED', 'READ'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;")
    op.create_table(
        'notification_preferences',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('in_app_enabled', sa.Boolean(), nullable=False),
        sa.Column('email_enabled', sa.Boolean(), nullable=False),
        sa.Column('push_enabled', sa.Boolean(), nullable=False),
        sa.Column('telegram_enabled', sa.Boolean(), nullable=False),
        sa.Column('schedule_enabled', sa.Boolean(), nullable=False),
        sa.Column('lesson_enabled', sa.Boolean(), nullable=False),
        sa.Column('homework_enabled', sa.Boolean(), nullable=False),
        sa.Column('homework_result_enabled', sa.Boolean(), nullable=False),
        sa.Column('chat_enabled', sa.Boolean(), nullable=False),
        sa.Column('news_enabled', sa.Boolean(), nullable=False),
        sa.Column('quiet_hours_enabled', sa.Boolean(), nullable=False),
        sa.Column('quiet_hours_start', sa.Time()),
        sa.Column('quiet_hours_end', sa.Time()),
        sa.Column('timezone', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('user_id', name='uq_notification_preference_user'),
    )
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('notification_type', _EnumType("notification_type_enum"), nullable=False),
        sa.Column('priority', _EnumType("notification_priority_enum"), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('source_service', sa.String(length=100), nullable=False),
        sa.Column('event_type', sa.String(length=150), nullable=False),
        sa.Column('source_entity_type', sa.String(length=100)),
        sa.Column('source_entity_id', sa.Integer()),
        sa.Column('payload', sa.JSON()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime()),
    )
    op.create_table(
        'notification_recipients',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('notification_id', sa.Integer(), sa.ForeignKey('notifications.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('channel', _EnumType("notification_channel_enum"), nullable=False),
        sa.Column('status', _EnumType("notification_status_enum"), nullable=False),
        sa.Column('delivered_at', sa.DateTime()),
        sa.Column('read_at', sa.DateTime()),
        sa.Column('error_message', sa.String(length=1000)),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('notification_id', 'user_id', 'channel', name='uq_notification_recipient_notification_user_channel'),
    )
    op.create_index('ix_notifications_expires_at', 'notifications', ['expires_at'], unique=False)
    op.create_index('ix_notifications_id', 'notifications', ['id'], unique=False)
    op.create_index('ix_notifications_priority', 'notifications', ['priority'], unique=False)
    op.create_index('ix_notifications_source_entity_type', 'notifications', ['source_entity_type'], unique=False)
    op.create_index('ix_notifications_event_type', 'notifications', ['event_type'], unique=False)
    op.create_index('ix_notifications_source_entity_id', 'notifications', ['source_entity_id'], unique=False)
    op.create_index('ix_notifications_source_service', 'notifications', ['source_service'], unique=False)
    op.create_index('ix_notifications_notification_type', 'notifications', ['notification_type'], unique=False)
    op.create_index('ix_notifications_created_at', 'notifications', ['created_at'], unique=False)
    op.create_index('ix_notification_preferences_id', 'notification_preferences', ['id'], unique=False)
    op.create_index('ix_notification_preferences_user_id', 'notification_preferences', ['user_id'], unique=True)
    op.create_index('ix_notification_recipients_user_id', 'notification_recipients', ['user_id'], unique=False)
    op.create_index('ix_notification_recipients_read_at', 'notification_recipients', ['read_at'], unique=False)
    op.create_index('ix_notification_recipients_channel', 'notification_recipients', ['channel'], unique=False)
    op.create_index('ix_notification_recipients_notification_id', 'notification_recipients', ['notification_id'], unique=False)
    op.create_index('ix_notification_recipients_status', 'notification_recipients', ['status'], unique=False)
    op.create_index('ix_notification_recipients_id', 'notification_recipients', ['id'], unique=False)

def downgrade() -> None:
    # Baseline downgrades are intentionally non-destructive.
    pass
