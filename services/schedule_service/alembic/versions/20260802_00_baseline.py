"""Immutable schedule_service schema baseline."""
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
    op.execute("DO $$ BEGIN CREATE TYPE lesson_type_enum AS ENUM ('REGULAR', 'EXTRA', 'REPLACEMENT', 'CONSULTATION', 'EXAM'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE lesson_status_enum AS ENUM ('SCHEDULED', 'COMPLETED', 'CANCELLED', 'RESCHEDULED'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE schedule_change_type_enum AS ENUM ('RESCHEDULED', 'CANCELLED', 'TEACHER_CHANGED', 'ROOM_CHANGED', 'UPDATED', 'RESTORED'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE attendance_status_enum AS ENUM ('PRESENT', 'REMOTE', 'ABSENT', 'LATE', 'EXCUSED'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;")
    op.create_table(
        'rooms',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('branch_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('capacity', sa.Integer()),
        sa.Column('description', sa.Text()),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_table(
        'schedule_templates',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('teacher_id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), sa.ForeignKey('rooms.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('weekday', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('lesson_type', _EnumType("lesson_type_enum"), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint('weekday >= 0 AND weekday <= 6', name='check_schedule_template_weekday'),
        sa.UniqueConstraint('group_id', 'weekday', 'start_time', name='uq_schedule_template_group_weekday_time'),
        sa.CheckConstraint('end_time > start_time', name='check_schedule_template_time'),
    )
    op.create_table(
        'lesson_schedules',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('teacher_id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), sa.ForeignKey('rooms.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('template_id', sa.Integer(), sa.ForeignKey('schedule_templates.id', ondelete='SET NULL')),
        sa.Column('lesson_date', sa.Date(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('status', _EnumType("lesson_status_enum"), nullable=False),
        sa.Column('lesson_type', _EnumType("lesson_type_enum"), nullable=False),
        sa.Column('topic', sa.String(length=255)),
        sa.Column('description', sa.Text()),
        sa.Column('is_extra', sa.Boolean(), nullable=False),
        sa.Column('created_by', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint('end_time > start_time', name='check_lesson_schedule_time'),
    )
    op.create_table(
        'attendance',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('lesson_id', sa.Integer(), sa.ForeignKey('lesson_schedules.id', ondelete='CASCADE'), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('status', _EnumType("attendance_status_enum"), nullable=False),
        sa.Column('late_minutes', sa.Integer(), nullable=False),
        sa.Column('comment', sa.String(length=1000)),
        sa.Column('marked_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('lesson_id', 'student_id', name='uq_attendance_lesson_student'),
        sa.CheckConstraint('late_minutes >= 0', name='check_attendance_late_minutes'),
    )
    op.create_table(
        'schedule_changes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('lesson_id', sa.Integer(), sa.ForeignKey('lesson_schedules.id', ondelete='CASCADE'), nullable=False),
        sa.Column('change_type', _EnumType("schedule_change_type_enum"), nullable=False),
        sa.Column('old_data', sa.JSON()),
        sa.Column('new_data', sa.JSON()),
        sa.Column('reason', sa.Text()),
        sa.Column('changed_by', sa.Integer(), nullable=False),
        sa.Column('comment', sa.String(length=500)),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_rooms_id', 'rooms', ['id'], unique=False)
    op.create_index('ix_rooms_branch_id', 'rooms', ['branch_id'], unique=False)
    op.create_index('ix_schedule_templates_weekday', 'schedule_templates', ['weekday'], unique=False)
    op.create_index('ix_schedule_templates_room_id', 'schedule_templates', ['room_id'], unique=False)
    op.create_index('ix_schedule_templates_group_id', 'schedule_templates', ['group_id'], unique=False)
    op.create_index('ix_schedule_templates_is_active', 'schedule_templates', ['is_active'], unique=False)
    op.create_index('ix_schedule_templates_id', 'schedule_templates', ['id'], unique=False)
    op.create_index('ix_schedule_templates_teacher_id', 'schedule_templates', ['teacher_id'], unique=False)
    op.create_index('ix_lesson_schedules_lesson_date', 'lesson_schedules', ['lesson_date'], unique=False)
    op.create_index('ix_lesson_schedules_teacher_id', 'lesson_schedules', ['teacher_id'], unique=False)
    op.create_index('ix_lesson_schedules_created_by', 'lesson_schedules', ['created_by'], unique=False)
    op.create_index('ix_lesson_schedules_template_id', 'lesson_schedules', ['template_id'], unique=False)
    op.create_index('ix_lesson_schedules_status', 'lesson_schedules', ['status'], unique=False)
    op.create_index('ix_lesson_schedules_room_id', 'lesson_schedules', ['room_id'], unique=False)
    op.create_index('ix_lesson_schedules_id', 'lesson_schedules', ['id'], unique=False)
    op.create_index('ix_lesson_schedules_group_id', 'lesson_schedules', ['group_id'], unique=False)
    op.create_index('ix_schedule_changes_id', 'schedule_changes', ['id'], unique=False)
    op.create_index('ix_schedule_changes_changed_by', 'schedule_changes', ['changed_by'], unique=False)
    op.create_index('ix_schedule_changes_lesson_id', 'schedule_changes', ['lesson_id'], unique=False)
    op.create_index('ix_schedule_changes_created_at', 'schedule_changes', ['created_at'], unique=False)
    op.create_index('ix_schedule_changes_change_type', 'schedule_changes', ['change_type'], unique=False)
    op.create_index('ix_attendance_student_status', 'attendance', ['student_id', 'status'], unique=False)
    op.create_index('ix_attendance_id', 'attendance', ['id'], unique=False)
    op.create_index('ix_attendance_lesson_id', 'attendance', ['lesson_id'], unique=False)
    op.create_index('ix_attendance_status', 'attendance', ['status'], unique=False)
    op.create_index('ix_attendance_marked_by', 'attendance', ['marked_by'], unique=False)
    op.create_index('ix_attendance_student_id', 'attendance', ['student_id'], unique=False)

def downgrade() -> None:
    # Baseline downgrades are intentionally non-destructive.
    pass
