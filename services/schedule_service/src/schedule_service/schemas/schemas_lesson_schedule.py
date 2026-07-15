from datetime import date, datetime, time

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator
)

from common.utils.enum_lesson_status import LessonStatus
from common.utils.enum_lesson_type import LessonType


# =====================================================
# Базовая схема конкретного занятия
# =====================================================

class LessonScheduleBase(BaseModel):
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

    template_id: int | None = Field(
        default=None,
        gt=0,
        description="ID недельного шаблона"
    )

    lesson_date: date = Field(
        ...,
        description="Дата занятия"
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

    topic: str | None = Field(
        default=None,
        max_length=255,
        description="Тема занятия"
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
        description="Описание занятия"
    )

    is_extra: bool = Field(
        default=False,
        description="Является ли занятие дополнительным"
    )

    created_by: int | None = Field(
        default=None,
        gt=0,
        description="ID пользователя, создавшего занятие"
    )

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.end_time <= self.start_time:
            raise ValueError(
                "Время окончания должно быть позже времени начала"
            )

        return self


# =====================================================
# Создание занятия
# =====================================================

class LessonScheduleCreate(LessonScheduleBase):
    pass


# =====================================================
# Частичное изменение занятия
# =====================================================

class LessonScheduleUpdate(BaseModel):
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

    template_id: int | None = Field(
        default=None,
        gt=0
    )

    lesson_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None

    lesson_type: LessonType | None = None

    topic: str | None = Field(
        default=None,
        max_length=255
    )

    description: str | None = Field(
        default=None,
        max_length=5000
    )

    is_extra: bool | None = None

    changed_by: int = Field(
        ...,
        gt=0,
        description="ID пользователя, изменившего занятие"
    )

    reason: str | None = Field(
        default=None,
        max_length=1000,
        description="Причина изменения"
    )


# =====================================================
# Отмена занятия
# =====================================================

class LessonCancelRequest(BaseModel):
    changed_by: int = Field(
        ...,
        gt=0
    )

    reason: str = Field(
        ...,
        min_length=1,
        max_length=1000
    )


# =====================================================
# Завершение занятия
# =====================================================

class LessonCompleteRequest(BaseModel):
    changed_by: int = Field(
        ...,
        gt=0
    )

    reason: str | None = Field(
        default=None,
        max_length=1000
    )


# =====================================================
# Перенос занятия
# =====================================================

class LessonRescheduleRequest(BaseModel):
    lesson_date: date
    start_time: time
    end_time: time

    room_id: int | None = Field(
        default=None,
        gt=0
    )

    teacher_id: int | None = Field(
        default=None,
        gt=0
    )

    changed_by: int = Field(
        ...,
        gt=0
    )

    reason: str = Field(
        ...,
        min_length=1,
        max_length=1000
    )

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.end_time <= self.start_time:
            raise ValueError(
                "Время окончания должно быть позже времени начала"
            )

        return self


# =====================================================
# Ответ API
# =====================================================

class LessonScheduleResponse(BaseModel):
    id: int

    group_id: int
    teacher_id: int
    room_id: int
    template_id: int | None

    lesson_date: date
    start_time: time
    end_time: time

    status: LessonStatus
    lesson_type: LessonType

    topic: str | None
    description: str | None

    is_extra: bool
    created_by: int | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =====================================================
# Ответ со списком занятий
# =====================================================

class LessonScheduleListResponse(BaseModel):
    total: int
    items: list[LessonScheduleResponse]