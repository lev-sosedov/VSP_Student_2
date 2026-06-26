from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from academic_service.db.base import Base


# группы
class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True) # личный идентификационный номер
    name = Column(String(150), nullable=False) # название группы
    branch_id = Column(Integer, nullable=False) # филиал id
    direction_id = Column(Integer, nullable=False)  # направление обучения id
    education_plan_id = Column(Integer, nullable=False) # учебный план id

    start_date = Column(DateTime, nullable=False) # дата начала обучения
    end_date = Column(DateTime, nullable=True) # дата окончания обучения

    is_active = Column(Boolean, default=True) # группа активна
    created_at = Column(DateTime, default=datetime.utcnow) # Дата создания
    closed_at = Column(DateTime, nullable=True) # Дата закрытия

    branch = relationship("Branch", back_populates="groups") # связь с филиалом
    direction = relationship("Direction", back_populates="groups") # связь с направлением
    education_plan = relationship("EducationPlan", back_populates="groups") # связь с учебным планом
    members = relationship("GroupMember", back_populates="group") # связь с участниками группы

