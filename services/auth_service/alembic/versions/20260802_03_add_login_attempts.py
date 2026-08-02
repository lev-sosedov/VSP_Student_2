"""add safe login attempt audit"""
from alembic import op
import sqlalchemy as sa
revision = "20260802_03"
down_revision = "20260802_02"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table("login_attempts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("occurred_at", sa.DateTime(), nullable=False),
        sa.Column("phone_hash", sa.String(64), nullable=False),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("ip_address", sa.String(64)),
        sa.Column("user_agent", sa.String(512)),
        sa.Column("reason_code", sa.String(64), nullable=False),
        sa.Column("auth_user_id", sa.Integer()))
    op.create_index("ix_login_attempts_phone_hash", "login_attempts", ["phone_hash"])
    op.create_index("ix_login_attempts_auth_user_id", "login_attempts", ["auth_user_id"])

def downgrade() -> None:
    op.drop_index("ix_login_attempts_auth_user_id", table_name="login_attempts")
    op.drop_index("ix_login_attempts_phone_hash", table_name="login_attempts")
    op.drop_table("login_attempts")
