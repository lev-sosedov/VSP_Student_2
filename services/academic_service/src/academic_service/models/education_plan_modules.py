from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship

from academic_service.db.base import Base


# Связь учебного плана и модулей
class EducationPlanModule(Base):
    __tablename__ = "education_plan_modules"


    id = Column(Integer, primary_key=True, index=True) # личный идентификационный номер
    education_plan_id = Column(Integer, nullable=False) # учебный план id
    module_id = Column(Integer, nullable=False) # модуль id
    order_number = Column(Integer, nullable=False) # порядок прохождения модуля

    education_plan = relationship("EducationPlan", back_populates="modules") # связь с учебным планом
    module = relationship("Module", back_populates="plans") # связь с модулем