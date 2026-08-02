"""Immutable academic_service schema baseline."""
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
    op.create_table(
        'branch_addresses',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('country', sa.String(length=100), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('street', sa.String(length=150), nullable=False),
        sa.Column('house', sa.String(length=20), nullable=False),
        sa.Column('building', sa.String(length=20)),
        sa.Column('postal_code', sa.String(length=20)),
    )
    op.create_table(
        'directions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('is_active', sa.Boolean()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('closed_at', sa.DateTime()),
    )
    op.create_table(
        'modules',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('is_active', sa.Boolean()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('closed_at', sa.DateTime()),
        sa.UniqueConstraint('name'),
    )
    op.create_table(
        'branches',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('branch_address_id', sa.Integer(), sa.ForeignKey('branch_addresses.id'), nullable=False),
        sa.Column('phone', sa.String(length=20)),
        sa.Column('email', sa.String(length=100)),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('closed_at', sa.DateTime()),
        sa.UniqueConstraint('email'),
    )
    op.create_table(
        'education_plans',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('direction_id', sa.Integer(), sa.ForeignKey('directions.id'), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('duration_months', sa.Integer(), nullable=False),
        sa.Column('lessons_per_week', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('closed_at', sa.DateTime()),
    )
    op.create_table(
        'education_plan_modules',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('education_plan_id', sa.Integer(), sa.ForeignKey('education_plans.id'), nullable=False),
        sa.Column('module_id', sa.Integer(), sa.ForeignKey('modules.id'), nullable=False),
        sa.Column('order_number', sa.Integer(), nullable=False),
    )
    op.create_table(
        'groups',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('branch_id', sa.Integer(), sa.ForeignKey('branches.id'), nullable=False),
        sa.Column('direction_id', sa.Integer(), sa.ForeignKey('directions.id'), nullable=False),
        sa.Column('education_plan_id', sa.Integer(), sa.ForeignKey('education_plans.id'), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime()),
        sa.Column('is_active', sa.Boolean()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('closed_at', sa.DateTime()),
    )
    op.create_table(
        'group_members',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('group_id', sa.Integer(), sa.ForeignKey('groups.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('joined_at', sa.DateTime()),
        sa.Column('left_at', sa.DateTime()),
        sa.Column('is_active', sa.Boolean()),
    )
    op.create_index('ix_branches_id', 'branches', ['id'], unique=False)
    op.create_index('ix_branch_addresses_id', 'branch_addresses', ['id'], unique=False)
    op.create_index('ix_directions_id', 'directions', ['id'], unique=False)
    op.create_index('ix_education_plans_id', 'education_plans', ['id'], unique=False)
    op.create_index('ix_education_plan_modules_id', 'education_plan_modules', ['id'], unique=False)
    op.create_index('ix_modules_id', 'modules', ['id'], unique=False)
    op.create_index('ix_groups_id', 'groups', ['id'], unique=False)
    op.create_index('ix_group_members_id', 'group_members', ['id'], unique=False)

def downgrade() -> None:
    # Baseline downgrades are intentionally non-destructive.
    pass
