from datetime import datetime
from sqlalchemy import Column, Integer, Boolean, DateTime, String
from sqlalchemy.orm import relationship

from academic_service.db.base import Base


# участники групп
class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True, index=True) # личный идентификационный
    group_id = Column(Integer, nullable=False) # группа id
    user_id = Column(Integer, nullable=False) # пользователь id
    role = Column(String(50), nullable=False) # роль пользователя
    joined_at = Column(DateTime, default=datetime.utcnow) # дата вступления в группу
    left_at = Column(DateTime, nullable=True) # дата отчисления из группы
    is_active = Column(Boolean,default=True) # Действующее или нет


    id = Column(Integer, primary_key=True, index=True) # личный идентификационный номер


    group_id = Column(Integer, nullable=False) # группа id


    user_id = Column(Integer, nullable=False) # пользователь id


    role = Column(String(50), nullable=False) # роль student teacher


    joined_at = Column(DateTime, default=datetime.utcnow) # дата вступления


    left_at = Column(DateTime, nullable=True) # дата выхода


    is_active = Column(Boolean, default=True) # активный участник


    group = relationship("Group", back_populates="members") # группа