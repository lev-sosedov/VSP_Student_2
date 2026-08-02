"""Immutable communication_service schema baseline."""
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
    op.execute("DO $$ BEGIN CREATE TYPE chat_type_enum AS ENUM ('PRIVATE', 'GROUP', 'LESSON', 'SUPPORT', 'CUSTOM'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE chat_member_role_enum AS ENUM ('OWNER', 'ADMIN', 'MEMBER', 'READ_ONLY'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE message_type_enum AS ENUM ('TEXT', 'SYSTEM', 'FILE', 'IMAGE', 'VIDEO', 'AUDIO'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE message_attachment_type_enum AS ENUM ('FILE', 'IMAGE', 'VIDEO', 'AUDIO', 'DOCUMENT', 'ARCHIVE', 'OTHER'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;")
    op.create_table(
        'chats',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('chat_type', _EnumType("chat_type_enum"), nullable=False),
        sa.Column('title', sa.String(length=255)),
        sa.Column('description', sa.Text()),
        sa.Column('group_id', sa.Integer()),
        sa.Column('lesson_id', sa.Integer()),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_archived', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('participant_one_id', sa.Integer()),
        sa.Column('participant_two_id', sa.Integer()),
    )
    op.create_table(
        'chat_members',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('chat_id', sa.Integer(), sa.ForeignKey('chats.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('member_role', _EnumType("chat_member_role_enum"), nullable=False),
        sa.Column('added_by', sa.Integer()),
        sa.Column('joined_at', sa.DateTime(), nullable=False),
        sa.Column('left_at', sa.DateTime()),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_muted', sa.Boolean(), nullable=False),
        sa.Column('is_pinned', sa.Boolean(), nullable=False),
        sa.Column('last_read_message_id', sa.Integer()),
        sa.UniqueConstraint('chat_id', 'user_id', name='uq_chat_member_chat_user'),
    )
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('chat_id', sa.Integer(), sa.ForeignKey('chats.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('message_type', _EnumType("message_type_enum"), nullable=False),
        sa.Column('text', sa.Text()),
        sa.Column('reply_to_message_id', sa.Integer(), sa.ForeignKey('messages.id', ondelete='SET NULL')),
        sa.Column('is_edited', sa.Boolean(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('is_pinned', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('edited_at', sa.DateTime()),
        sa.Column('deleted_at', sa.DateTime()),
    )
    op.create_table(
        'message_attachments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('message_id', sa.Integer(), sa.ForeignKey('messages.id', ondelete='CASCADE'), nullable=False),
        sa.Column('attachment_type', _EnumType("message_attachment_type_enum"), nullable=False),
        sa.Column('file_url', sa.String(length=3000), nullable=False),
        sa.Column('file_name', sa.String(length=255)),
        sa.Column('mime_type', sa.String(length=150)),
        sa.Column('file_size', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_table(
        'message_reads',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('message_id', sa.Integer(), sa.ForeignKey('messages.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('read_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('message_id', 'user_id', name='uq_message_read_message_user'),
    )
    op.create_index('ix_chats_group_id', 'chats', ['group_id'], unique=False)
    op.create_index('ix_chats_created_at', 'chats', ['created_at'], unique=False)
    op.create_index('ix_chats_participant_one_id', 'chats', ['participant_one_id'], unique=False)
    op.create_index('ix_chats_chat_type', 'chats', ['chat_type'], unique=False)
    op.create_index('ix_chats_created_by', 'chats', ['created_by'], unique=False)
    op.create_index('ix_chats_participant_two_id', 'chats', ['participant_two_id'], unique=False)
    op.create_index('ix_chats_id', 'chats', ['id'], unique=False)
    op.create_index('ix_chats_lesson_id', 'chats', ['lesson_id'], unique=False)
    op.create_index('ix_chats_is_active', 'chats', ['is_active'], unique=False)
    op.create_index('ix_chats_is_archived', 'chats', ['is_archived'], unique=False)
    op.create_index('ix_chat_members_user_id', 'chat_members', ['user_id'], unique=False)
    op.create_index('ix_chat_members_chat_id', 'chat_members', ['chat_id'], unique=False)
    op.create_index('ix_chat_members_is_active', 'chat_members', ['is_active'], unique=False)
    op.create_index('ix_chat_members_id', 'chat_members', ['id'], unique=False)
    op.create_index('ix_chat_members_member_role', 'chat_members', ['member_role'], unique=False)
    op.create_index('ix_messages_sender_id', 'messages', ['sender_id'], unique=False)
    op.create_index('ix_messages_id', 'messages', ['id'], unique=False)
    op.create_index('ix_messages_message_type', 'messages', ['message_type'], unique=False)
    op.create_index('ix_messages_is_deleted', 'messages', ['is_deleted'], unique=False)
    op.create_index('ix_messages_chat_id', 'messages', ['chat_id'], unique=False)
    op.create_index('ix_messages_is_pinned', 'messages', ['is_pinned'], unique=False)
    op.create_index('ix_messages_reply_to_message_id', 'messages', ['reply_to_message_id'], unique=False)
    op.create_index('ix_messages_created_at', 'messages', ['created_at'], unique=False)
    op.create_index('ix_message_attachments_message_id', 'message_attachments', ['message_id'], unique=False)
    op.create_index('ix_message_attachments_id', 'message_attachments', ['id'], unique=False)
    op.create_index('ix_message_attachments_attachment_type', 'message_attachments', ['attachment_type'], unique=False)
    op.create_index('ix_message_reads_id', 'message_reads', ['id'], unique=False)
    op.create_index('ix_message_reads_user_id', 'message_reads', ['user_id'], unique=False)
    op.create_index('ix_message_reads_message_id', 'message_reads', ['message_id'], unique=False)
    op.create_index('uq_private_chat_canonical_pair', 'chats', ['participant_one_id', 'participant_two_id'], unique=True, postgresql_where=sa.text("chat_type = 'PRIVATE' AND participant_one_id IS NOT NULL AND participant_two_id IS NOT NULL"))

def downgrade() -> None:
    # Baseline downgrades are intentionally non-destructive.
    pass
