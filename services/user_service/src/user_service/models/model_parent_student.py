from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship as orm_relationship
from common.utils.enum_role import RoleType
from user_service.db.db_base import Base


class ParentStudentLink(Base):
    """
    Связь родителя со студентом.

    Один родитель может иметь несколько детей.
    Один студент может быть связан с несколькими родителями.
    """

    __tablename__ = "parent_student_links"

    __table_args__ = (
        UniqueConstraint(
            "parent_id",
            "student_id",
            name="uq_parent_student_link",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    parent_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    student_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    relationship = Column(
        String(30),
        nullable=False,
        default="guardian",
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    parent = orm_relationship(
        "User",
        foreign_keys=[parent_id],
        back_populates="children_links",
    )

    student = orm_relationship(
        "User",
        foreign_keys=[student_id],
        back_populates="parent_links",
    )