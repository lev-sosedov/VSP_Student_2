"""Add token version for future server-side token invalidation."""

from alembic import op
import sqlalchemy as sa

revision = "20260802_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "auth_users",
        sa.Column("token_version", sa.Integer(), server_default="1", nullable=True),
    )
    op.execute(sa.text("UPDATE auth_users SET token_version = 1 WHERE token_version IS NULL"))
    op.alter_column(
        "auth_users",
        "token_version",
        existing_type=sa.Integer(),
        nullable=False,
        server_default="1",
    )
    op.create_check_constraint(
        "ck_auth_users_token_version_positive",
        "auth_users",
        "token_version >= 1",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_auth_users_token_version_positive",
        "auth_users",
        type_="check",
    )
    op.drop_column("auth_users", "token_version")
