from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Integer,
    String,
    Text
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from common.utils.enum_post_status import (
    PostStatus
)
from common.utils.enum_post_type import (
    PostType
)
from news_service.db.db_base import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    post_type: Mapped[PostType] = mapped_column(
        Enum(
            PostType,
            name="post_type_enum",
            values_callable=lambda enum_class: [
                item.value
                for item in enum_class
            ]
        ),
        default=PostType.POST,
        nullable=False,
        index=True
    )

    status: Mapped[PostStatus] = mapped_column(
        Enum(
            PostStatus,
            name="post_status_enum",
            values_callable=lambda enum_class: [
                item.value
                for item in enum_class
            ]
        ),
        default=PostStatus.DRAFT,
        nullable=False,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    slug: Mapped[str] = mapped_column(
        String(600),
        nullable=False,
        unique=True,
        index=True
    )

    summary: Mapped[str | None] = mapped_column(
        String(1500),
        nullable=True
    )

    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Категория для фильтров на странице.
    # Например: school-life, education, events.
    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )

    # Обложка нужна для карточки в Pinterest-сетке.
    cover_media_url: Mapped[str | None] = mapped_column(
        String(3000),
        nullable=True
    )

    cover_media_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    cover_preview_url: Mapped[str | None] = mapped_column(
        String(3000),
        nullable=True
    )

    cover_width: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    cover_height: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    created_by: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )

    updated_by: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    published_by: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    is_pinned: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )

    allow_comments: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    # Администратор сам решает,
    # отправлять ли уведомления о публикации.
    send_notification: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    views_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    comments_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True
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

    media = relationship(
        "PostMedia",
        back_populates="post",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="PostMedia.sort_order"
    )

    views = relationship(
        "PostView",
        back_populates="post",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    comments = relationship(
        "PostComment",
        back_populates="post",
        cascade="all, delete-orphan",
        passive_deletes=True
    )