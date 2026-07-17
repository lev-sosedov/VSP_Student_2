from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from news_service.db.db_base import Base


class PostView(Base):
    __tablename__ = "post_views"

    __table_args__ = (
        UniqueConstraint(
            "post_id",
            "user_id",
            name="uq_post_view_post_user"
        ),
    )

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

    user_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )

    viewed_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    post = relationship(
        "Post",
        back_populates="views"
    )