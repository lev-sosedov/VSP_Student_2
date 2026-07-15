from datetime import datetime, time

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator
)

from common.utils.enum_lesson_type import LessonType


# =====================================================
# Базовая схема шаблона расписания
# =====================================================

class ScheduleTemplateBase(BaseModel):
    group_id: int = Field(
        ...,
        gt=0,
        description="ID группы из academic-service"
    )

    teacher_id: int = Field(
        ...,
        gt=0,
        description="ID преподавателя из user-service"
    )

    room_id: int = Field(
        ...,
        gt=0,
        description="ID кабинета из schedule-service"
    )

    weekday: int = Field(
        ...,
        ge=0,
        le=6,
        description=(
            "День недели: "
            "0 — понедельник, "
            "1 — вторник, "
            "2 — среда, "
            "3 — четверг, "
            "4 — пятница, "
            "5 — суббота, "
            "6 — воскресенье"
        )
    )

    start_time: time = Field(
        ...,
        description="Время начала занятия"
    )

    end_time: time = Field(
        ...,
        description="Время окончания занятия"
    )

    lesson_type: LessonType = Field(
        default=LessonType.REGULAR,
        description="Тип занятия"
    )

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.end_time <= self.start_time:
            raise ValueError(
                "Время окончания должно быть позже времени начала"
            )

        return self


# =====================================================
# Создание шаблона
# =====================================================

class ScheduleTemplateCreate(ScheduleTemplateBase):
    pass


# =====================================================
# Частичное изменение шаблона
# =====================================================

class ScheduleTemplateUpdate(BaseModel):
    group_id: int | None = Field(
        default=None,
        gt=0
    )

    teacher_id: int | None = Field(
        default=None,
        gt=0
    )

    room_id: int | None = Field(
        default=None,
        gt=0
    )

    weekday: int | None = Field(
        default=None,
        ge=0,
        le=6
    )

    start_time: time | None = None
    end_time: time | None = None

    lesson_type: LessonType | None = None

    is_active: bool | None = None


# =====================================================
# Ответ API
# =====================================================

class ScheduleTemplateResponse(ScheduleTemplateBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Ответ со списком шаблонов
# =====================================================

class ScheduleTemplateListResponse(BaseModel):
    total: int
    items: list[ScheduleTemplateResponse]