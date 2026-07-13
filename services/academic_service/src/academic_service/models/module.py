from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship

from academic_service.db.base import Base


# Модуль
class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)  # личный идентификационный
    name = Column(String(150), nullable=False, unique=True)  # название модуля
    description = Column(Text, nullable=True)  # описание модуля

    plans = relationship("EducationPlanModule", back_populates="module")  # связь с учебными планами

    is_active = Column(Boolean, default=True)  # модуль активен
    created_at = Column(DateTime, default=datetime.utcnow)  # дата создания
    closed_at = Column(DateTime, nullable=True)  # Дата закрытия