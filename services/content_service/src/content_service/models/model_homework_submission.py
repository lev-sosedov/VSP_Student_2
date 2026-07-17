from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Text, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.utils.enum_homework_submission_status import (
    HomeworkSubmissionStatus
)
from content_service.db.db_base import Base


# =====================================================
# Работа студента по домашнему заданию
# =====================================================

class HomeworkSubmission(Base):
    __tablename__ = "homework_submissions"

    __table_args__ = (
        CheckConstraint(
            "score IS NULL OR score >= 0",
            name="check_homework_submission_score_positive"
        ),
        UniqueConstraint(
            "homework_id",
            "student_id",
            name="uq_homework_submission_homework_student"
        ),
    )

    # Личный идентификатор работы
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    # ID домашнего задания внутри content-service
    homework_id: Mapped[int] = mapped_column(
        ForeignKey(
            "homeworks.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    # ID студента из user-service
    #
    # ForeignKey не ставим, потому что пользователь
    # находится в другом микросервисе и другой базе.
    student_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )

    # Текстовый ответ студента
    answer_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Статус работы
    status: Mapped[HomeworkSubmissionStatus] = mapped_column(
        Enum(
            HomeworkSubmissionStatus,
            name="homework_submission_status_enum"
        ),
        default=HomeworkSubmissionStatus.DRAFT,
        nullable=False,
        index=True
    )

    # Набранные баллы
    score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    # Комментарий преподавателя
    teacher_comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # ID преподавателя, проверившего работу
    checked_by: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True
    )

    # Отправлена ли работа после срока
    is_late: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )

    # Дата первой отправки работы
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True
    )

    # Дата проверки преподавателем
    checked_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    # Дата создания черновика
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Дата последнего изменения
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Связь с домашним заданием
    homework = relationship(
        "Homework",
        back_populates="submissions"
    )

    # Файлы, которые загрузил студент
    attachments = relationship(
        "SubmissionAttachment",
        back_populates="submission",
        cascade="all, delete-orphan",
        passive_deletes=True
    )