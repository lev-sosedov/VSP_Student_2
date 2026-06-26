from sqlalchemy import Column, Integer, String

from academic_service.db.base import Base


# Адрес филиала
class BranchAddress(Base):
    __tablename__ = "branch_addresses"

    id = Column(Integer, primary_key=True, index=True) # личный идентификационный номер
    country = Column(String(100), nullable=False) # Страна
    city = Column(String(100), nullable=False) # Город
    street = Column(String(150), nullable=False) # Улица
    house = Column(String(20), nullable=False) # номер дома
    building = Column(String(20), nullable=True) # Корпус
    postal_code = Column(String(20), nullable=True) # почтовый индекс
