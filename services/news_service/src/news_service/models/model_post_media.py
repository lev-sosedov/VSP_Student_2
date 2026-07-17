from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from common.utils.enum_post_media_type import (
    PostMediaType
)
from news_service.db.db_base import Base


class PostMedia(Base):
    __tablename__ = "post_media"

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

    media_type: Mapped[PostMediaType] = mapped_column(
        Enum(
            PostMediaType,
            name="post_media_type_enum",
            values_callable=lambda enum_class: [
                item.value
                for item in enum_class
            ]
        ),
        nullable=False,
        index=True
    )

    file_url: Mapped[str] = mapped_column(
        String(3000),
        nullable=False
    )

    # Превью особенно важно для видео и аудио.
    preview_url: Mapped[str | None] = mapped_column(
        String(3000),
        nullable=True
    )

    file_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    mime_type: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    file_size: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    width: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    height: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    duration_seconds: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    alt_text: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    uploaded_by: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    post = relationship(
        "Post",
        back_populates="media"
    )