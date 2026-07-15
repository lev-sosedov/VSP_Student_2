from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


# =====================================================
# Базовая схема кабинета
# =====================================================

class RoomBase(BaseModel):
    branch_id: int = Field(
        ...,
        gt=0,
        description="ID филиала из academic-service"
    )

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Название или номер кабинета"
    )

    capacity: int | None = Field(
        default=None,
        gt=0,
        le=1000,
        description="Вместимость кабинета"
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
        description="Описание кабинета"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("Название кабинета не может быть пустым")

        return cleaned_value

    @field_validator("description")
    @classmethod
    def validate_description(
        cls,
        value: str | None
    ) -> str | None:
        if value is None:
            return None

        cleaned_value = value.strip()

        return cleaned_value or None


# =====================================================
# Создание кабинета
# =====================================================

class RoomCreate(RoomBase):
    pass


# =====================================================
# Частичное изменение кабинета
# =====================================================

class RoomUpdate(BaseModel):
    branch_id: int | None = Field(
        default=None,
        gt=0
    )

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    capacity: int | None = Field(
        default=None,
        gt=0,
        le=1000
    )

    description: str | None = Field(
        default=None,
        max_length=2000
    )

    is_active: bool | None = None

    @field_validator("name")
    @classmethod
    def validate_name(
        cls,
        value: str | None
    ) -> str | None:
        if value is None:
            return None

        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("Название кабинета не может быть пустым")

        return cleaned_value

    @field_validator("description")
    @classmethod
    def validate_description(
        cls,
        value: str | None
    ) -> str | None:
        if value is None:
            return None

        cleaned_value = value.strip()

        return cleaned_value or None


# =====================================================
# Ответ API
# =====================================================

class RoomResponse(RoomBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Ответ со списком кабинетов
# =====================================================

class RoomListResponse(BaseModel):
    total: int
    items: list[RoomResponse]