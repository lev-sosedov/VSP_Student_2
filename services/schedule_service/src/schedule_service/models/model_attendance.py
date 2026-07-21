from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.utils.enum_attendance_status import (
    AttendanceStatus,
)
from schedule_service.db.db_base import Base


class Attendance(Base):
    __tablename__ = "attendance"

    __table_args__ = (
        UniqueConstraint(
            "lesson_id",
            "student_id",
            name="uq_attendance_lesson_student",
        ),
        CheckConstraint(
            "late_minutes >= 0",
            name="check_attendance_late_minutes",
        ),
        Index(
            "ix_attendance_student_status",
            "student_id",
            "status",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # Конкретное занятие в schedule-service
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey(
            "lesson_schedules.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ID студента из user-service
    student_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    status: Mapped[AttendanceStatus] = mapped_column(
        Enum(
            AttendanceStatus,
            name="attendance_status_enum",
        ),
        nullable=False,
        default=AttendanceStatus.PRESENT,
        index=True,
    )

    late_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    comment: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    # ID преподавателя или администратора,
    # который поставил отметку
    marked_by: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    lesson = relationship(
        "LessonSchedule",
        back_populates="attendance_records",
    )