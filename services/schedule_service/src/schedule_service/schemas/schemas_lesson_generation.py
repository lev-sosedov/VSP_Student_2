from datetime import date

from pydantic import BaseModel, Field, model_validator


# =====================================================
# Запрос генерации занятий
# =====================================================

class LessonGenerationRequest(BaseModel):
    date_from: date = Field(
        ...,
        description="Начальная дата генерации"
    )

    date_to: date = Field(
        ...,
        description="Конечная дата генерации"
    )

    created_by: int = Field(
        ...,
        gt=0,
        description=(
            "ID пользователя, запустившего генерацию. "
            "Позже будет получаться из JWT"
        )
    )

    skip_conflicts: bool = Field(
        default=True,
        description=(
            "Пропускать конфликтующие занятия. "
            "Если False — вся операция завершится ошибкой "
            "при первом конфликте"
        )
    )

    topic: str | None = Field(
        default=None,
        max_length=255,
        description="Общая тема для созданных занятий"
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
        description="Общее описание для созданных занятий"
    )

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.date_to < self.date_from:
            raise ValueError(
                "Конечная дата не может быть раньше начальной"
            )

        period_days = (
            self.date_to - self.date_from
        ).days

        if period_days > 366:
            raise ValueError(
                "За один запрос можно сформировать "
                "занятия максимум на 366 дней"
            )

        return self


# =====================================================
# Информация о пропущенном занятии
# =====================================================

class LessonGenerationConflict(BaseModel):
    lesson_date: date
    reason: str
    conflict_lesson_id: int | None = None


# =====================================================
# Ответ генерации
# =====================================================

class LessonGenerationResponse(BaseModel):
    template_id: int

    date_from: date
    date_to: date

    created_count: int
    skipped_count: int

    created_lesson_ids: list[int]
    conflicts: list[LessonGenerationConflict]