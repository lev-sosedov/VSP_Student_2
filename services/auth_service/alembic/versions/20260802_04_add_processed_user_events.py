"""Add idempotency ledger for user synchronization events."""
from alembic import op
import sqlalchemy as sa

revision = "20260802_04"
down_revision = "20260802_03"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "processed_user_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.String(length=64), nullable=False),
        sa.Column("processed_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("event_id", name="uq_processed_user_events_event_id"),
    )
    op.create_index("ix_processed_user_events_event_id", "processed_user_events", ["event_id"], unique=True)


def downgrade():
    op.drop_index("ix_processed_user_events_event_id", table_name="processed_user_events")
    op.drop_table("processed_user_events")
