from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from academic_service.db.base import Base


# Учебный план 24, 365 и 60 месяцев
class EducationPlan(Base):
    __tablename__ = "education_plans"

    id = Column(Integer, primary_key=True, index=True)  # личный идентификационный номер
    direction_id = Column(Integer, ForeignKey("directions.id"), nullable=False)  # направление обучения id
    name = Column(String(150), nullable=False)  # название учебного плана
    duration_months = Column(Integer, nullable=False)  # длительность обучения в месяцах
    lessons_per_week = Column(Integer, nullable=False)  # количество занятий в неделю

    direction = relationship("Direction", back_populates="education_plans")  # связь с направлением
    modules = relationship("EducationPlanModule", back_populates="education_plan")  # связь с модулями учебного плана
    groups = relationship("Group", back_populates="education_plan")  # связь с группами

    is_active = Column(Boolean, default=True)  # учебный план активен
    created_at = Column(DateTime, default=datetime.utcnow)  # Дата создания
    closed_at = Column(DateTime, nullable=True)  # Дата закрытия