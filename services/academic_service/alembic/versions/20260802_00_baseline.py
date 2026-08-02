"""Initial academic-service schema baseline for new databases."""
from alembic import op
from academic_service.db.db_base import Base
from academic_service.db import db_init_models  # noqa: F401
from common.alembic_baseline import prepare_metadata, create_enum_types
revision = "20260802_00"
down_revision = None
branch_labels = None
depends_on = None
def upgrade() -> None:
    bind = op.get_bind()
    create_enum_types(bind, prepare_metadata(Base.metadata))
    Base.metadata.create_all(bind)
def downgrade() -> None:
    # Baselines are immutable schema declarations; never drop a populated DB.
    pass
