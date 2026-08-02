"""Track bounded, retryable transactional-outbox delivery state."""
from alembic import op
import sqlalchemy as sa

revision = "20260802_01"
down_revision = "20260802_00"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user_event_outbox", sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("user_event_outbox", sa.Column("next_attempt_at", sa.DateTime(), nullable=True))
    op.add_column("user_event_outbox", sa.Column("last_error_code", sa.String(length=64), nullable=True))
    op.create_index("ix_user_event_outbox_delivery", "user_event_outbox", ["published_at", "next_attempt_at"])


def downgrade() -> None:
    op.drop_index("ix_user_event_outbox_delivery", table_name="user_event_outbox")
    op.drop_column("user_event_outbox", "last_error_code")
    op.drop_column("user_event_outbox", "next_attempt_at")
    op.drop_column("user_event_outbox", "retry_count")
