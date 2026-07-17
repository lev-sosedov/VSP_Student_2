from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Text,
    Boolean
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from common.utils.enum_post_comment_status import (
    PostCommentStatus
)
from news_service.db.db_base import Base


class PostComment(Base):
    __tablename__ = "post_comments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    post_id: Mapped[int] = mapped_column(
        ForeignKey(
            "posts.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    author_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )

    # Позволяет отвечать на комментарии.
    parent_comment_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "post_comments.id",
            ondelete="CASCADE"
        ),
        nullable=True,
        index=True
    )

    text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    status: Mapped[
        PostCommentStatus
    ] = mapped_column(
        Enum(
            PostCommentStatus,
            name="post_comment_status_enum",
            values_callable=lambda enum_class: [
                item.value
                for item in enum_class
            ]
        ),
        default=PostCommentStatus.PUBLISHED,
        nullable=False,
        index=True
    )

    is_edited: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    edited_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    post = relationship(
        "Post",
        back_populates="comments"
    )

    parent = relationship(
        "PostComment",
        remote_side="PostComment.id",
        back_populates="replies"
    )

    replies = relationship(
        "PostComment",
        back_populates="parent",
        cascade="all, delete-orphan",
        single_parent=True,
        order_by="PostComment.created_at"
    )