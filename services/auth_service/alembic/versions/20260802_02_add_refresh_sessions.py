"""add persistent refresh sessions

Revision ID: 20260802_02
Revises: 20260802_01
"""
from alembic import op
import sqlalchemy as sa

revision = "20260802_02"
down_revision = "20260802_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "refresh_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("family_id", sa.String(length=64), nullable=False),
        sa.Column("auth_user_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("refresh_jti", sa.String(length=128), nullable=False),
        sa.Column("refresh_token_hash", sa.String(length=64), nullable=False),
        sa.Column("token_version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("last_used_at", sa.DateTime()),
        sa.Column("revoked_at", sa.DateTime()),
        sa.Column("replaced_by_session_id", sa.Integer()),
        sa.Column("revoke_reason", sa.String(length=128)),
        sa.Column("user_agent", sa.String(length=512)),
        sa.Column("ip_address", sa.String(length=64)),
    )
    op.create_index("ix_refresh_sessions_refresh_jti", "refresh_sessions", ["refresh_jti"], unique=True)
    op.create_index("ix_refresh_sessions_auth_user_active", "refresh_sessions", ["auth_user_id", "revoked_at"])
    op.create_index("ix_refresh_sessions_family_id", "refresh_sessions", ["family_id"])


def downgrade() -> None:
    op.drop_index("ix_refresh_sessions_auth_user_active", table_name="refresh_sessions")
    op.drop_index("ix_refresh_sessions_family_id", table_name="refresh_sessions")
    op.drop_index("ix_refresh_sessions_refresh_jti", table_name="refresh_sessions")
    op.drop_table("refresh_sessions")
