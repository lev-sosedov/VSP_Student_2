"""Initial communication schema, including canonical private-chat columns."""
from alembic import op
from communication_service.db.db_base import Base
from communication_service.db import db_init_models  # noqa: F401
from common.alembic_baseline import prepare_metadata, create_enum_types
revision = "20260802_00"
down_revision = None
branch_labels = None
depends_on = None
def upgrade() -> None:
    bind = op.get_bind()
    create_enum_types(bind, prepare_metadata(Base.metadata))
    Base.metadata.create_all(bind)
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_private_chat_canonical_pair ON chats (participant_one_id, participant_two_id) WHERE chat_type = 'PRIVATE' AND participant_one_id IS NOT NULL AND participant_two_id IS NOT NULL")
def downgrade() -> None: pass
