from datetime import datetime
from sqlalchemy import Column, Integer, Boolean, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship

from academic_service.db.base import Base


# участники групп
class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True, index=True)  # личный идентификационный
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)  # группа id
    user_id = Column(Integer, nullable=False)  # пользователь id
    role = Column(String(50), nullable=False)  # роль пользователя

    joined_at = Column(DateTime, default=datetime.utcnow)  # дата вступления в группу
    left_at = Column(DateTime, nullable=True)  # дата отчисления из группы
    is_active = Column(Boolean, default=True)  # Действующее или нет

    group = relationship("Group", back_populates="members")  # группа