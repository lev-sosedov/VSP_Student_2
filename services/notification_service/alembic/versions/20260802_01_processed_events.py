"""Durable idempotency markers for notification event consumers."""
from alembic import op
import sqlalchemy as sa

revision = "20260802_01"
down_revision = "20260802_00"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "processed_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=128), nullable=False),
        sa.Column("producer", sa.String(length=128), nullable=False),
        sa.Column("processed_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("event_id", name="uq_notification_processed_event_id"),
    )
    op.create_index("ix_notification_processed_events_event_id", "processed_events", ["event_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_notification_processed_events_event_id", table_name="processed_events")
    op.drop_table("processed_events")
