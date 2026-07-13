from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship

from academic_service.db.base import Base


# Направление обучения
class Direction(Base):
    __tablename__ = "directions"

    id = Column(Integer, primary_key=True, index=True)  # личный идентификационный номер
    name = Column(String(150), nullable=False)  # название направления
    description = Column(Text, nullable=True)  # описание направления

    education_plans = relationship("EducationPlan", back_populates="direction")  # связь с учебным планом
    groups = relationship("Group", back_populates="direction")  # связь с группы направления

    is_active = Column(Boolean, default=True)  # направление активно
    created_at = Column(DateTime, default=datetime.utcnow)  # дата создания
    closed_at = Column(DateTime, nullable=True)  # дата закрытия