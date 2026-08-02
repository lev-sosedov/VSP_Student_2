"""Transactional academic domain-event outbox."""
from alembic import op
import sqlalchemy as sa
revision="20260802_01"; down_revision="20260802_00"; branch_labels=None; depends_on=None
def upgrade():
    op.create_table("event_outbox", sa.Column("id",sa.Integer(),primary_key=True), sa.Column("event_id",sa.String(64),nullable=False), sa.Column("event_type",sa.String(128),nullable=False), sa.Column("event_version",sa.Integer(),nullable=False,server_default="1"), sa.Column("producer",sa.String(128),nullable=False), sa.Column("correlation_id",sa.String(64)), sa.Column("causation_id",sa.String(64)), sa.Column("payload",sa.Text(),nullable=False), sa.Column("created_at",sa.DateTime(),server_default=sa.func.now(),nullable=False), sa.Column("published_at",sa.DateTime()), sa.Column("retry_count",sa.Integer(),server_default="0",nullable=False), sa.Column("next_attempt_at",sa.DateTime()), sa.Column("last_error_code",sa.String(64)), sa.Column("claimed_at",sa.DateTime()), sa.Column("claimed_by",sa.String(64)), sa.UniqueConstraint("event_id",name="uq_academic_event_outbox_event_id"))
    op.create_index("ix_academic_event_outbox_delivery","event_outbox",["published_at","next_attempt_at"])
def downgrade():
    op.drop_index("ix_academic_event_outbox_delivery",table_name="event_outbox"); op.drop_table("event_outbox")
