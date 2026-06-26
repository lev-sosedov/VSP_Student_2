from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from academic_service.db.base import Base



# Филиал
class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True) # личный идентификационный номер
    branch_address_id = Column(Integer, nullable=False) # адрес филиала id
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True) # телефон филиала
    email = Column(String(100), unique=True, nullable=True)  # почта

    groups = relationship("Group", back_populates="branch") # связь с группы филиала
    branch_address = relationship("BranchAddress") # связь с адресом филиала

    is_active: Mapped[bool] = mapped_column(Boolean, default=True) # действующий филиал или закрыт
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow) # дата открытия филиала
    closed_at = Column(DateTime, nullable=True) # дата закрытия филиала
