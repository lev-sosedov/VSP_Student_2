from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common.utils.enum_lesson_status import LessonStatus

from schedule_service.models.model_lesson_schedule import LessonSchedule
from schedule_service.models.model_schedule_template import (
    ScheduleTemplate
)
from schedule_service.schemas.schemas_lesson_generation import (
    LessonGenerationConflict,
    LessonGenerationRequest,
    LessonGenerationResponse
)
from schedule_service.services.service_lesson_schedule import (
    find_lesson_conflict
)


# =====================================================
# Получение дат нужного дня недели
# =====================================================

def get_template_dates(
    date_from: date,
    date_to: date,
    weekday: int
) -> list[date]:
    """
    Возвращает все даты в указанном периоде,
    соответствующие дню недели шаблона.

    В Python:
    0 — понедельник
    1 — вторник
    2 — среда
    3 — четверг
    4 — пятница
    5 — суббота
    6 — воскресенье
    """

    days_until_weekday = (
        weekday - date_from.weekday()
    ) % 7

    current_date = (
        date_from
        + timedelta(days=days_until_weekday)
    )

    lesson_dates: list[date] = []

    while current_date <= date_to:
        lesson_dates.append(current_date)

        current_date += timedelta(days=7)

    return lesson_dates


# =====================================================
# Проверка уже созданного занятия этого шаблона
# =====================================================

async def get_generated_lesson(
    session: AsyncSession,
    template_id: int,
    lesson_date: date
) -> LessonSchedule | None:
    query = select(LessonSchedule).where(
        LessonSchedule.template_id == template_id,
        LessonSchedule.lesson_date == lesson_date,
        LessonSchedule.status.in_([
            LessonStatus.SCHEDULED,
            LessonStatus.RESCHEDULED,
            LessonStatus.COMPLETED
        ])
    )

    result = await session.execute(query)

    return result.scalar_one_or_none()


# =====================================================
# Формирование причины конфликта
# =====================================================

def get_generation_conflict_reason(
    conflict: LessonSchedule,
    template: ScheduleTemplate
) -> str:
    reasons: list[str] = []

    if conflict.group_id == template.group_id:
        reasons.append("группа уже занята")

    if conflict.teacher_id == template.teacher_id:
        reasons.append("преподаватель уже занят")

    if conflict.room_id == template.room_id:
        reasons.append("кабинет уже занят")

    if not reasons:
        return "обнаружен конфликт расписания"

    return ", ".join(reasons)


# =====================================================
# Генерация занятий по шаблону
# =====================================================

async def generate_lessons_from_template(
    session: AsyncSession,
    template: ScheduleTemplate,
    generation_data: LessonGenerationRequest
) -> LessonGenerationResponse:
    lesson_dates = get_template_dates(
        date_from=generation_data.date_from,
        date_to=generation_data.date_to,
        weekday=template.weekday
    )

    created_lesson_ids: list[int] = []
    conflicts: list[LessonGenerationConflict] = []

    for lesson_date in lesson_dates:

        # =============================================
        # Проверка повторной генерации по этому шаблону
        # =============================================

        existing_generated_lesson = await get_generated_lesson(
            session=session,
            template_id=template.id,
            lesson_date=lesson_date
        )

        if existing_generated_lesson is not None:
            conflicts.append(
                LessonGenerationConflict(
                    lesson_date=lesson_date,
                    reason=(
                        "Занятие по этому шаблону "
                        "на указанную дату уже создано"
                    ),
                    conflict_lesson_id=existing_generated_lesson.id
                )
            )

            if generation_data.skip_conflicts:
                continue

            raise ValueError(
                f"Занятие по шаблону уже существует "
                f"на дату {lesson_date.isoformat()}"
            )

        # =============================================
        # Проверка пересечений расписания
        # =============================================

        conflict = await find_lesson_conflict(
            session=session,
            group_id=template.group_id,
            teacher_id=template.teacher_id,
            room_id=template.room_id,
            lesson_date=lesson_date,
            start_time=template.start_time,
            end_time=template.end_time
        )

        if conflict is not None:
            conflict_reason = get_generation_conflict_reason(
                conflict=conflict,
                template=template
            )

            conflicts.append(
                LessonGenerationConflict(
                    lesson_date=lesson_date,
                    reason=conflict_reason,
                    conflict_lesson_id=conflict.id
                )
            )

            if generation_data.skip_conflicts:
                continue

            raise ValueError(
                f"Обнаружен конфликт на дату "
                f"{lesson_date.isoformat()}: "
                f"{conflict_reason}"
            )

        # =============================================
        # Создание конкретного занятия
        # =============================================

        lesson = LessonSchedule(
            group_id=template.group_id,
            teacher_id=template.teacher_id,
            room_id=template.room_id,
            template_id=template.id,
            lesson_date=lesson_date,
            start_time=template.start_time,
            end_time=template.end_time,
            status=LessonStatus.SCHEDULED,
            lesson_type=template.lesson_type,
            topic=generation_data.topic,
            description=generation_data.description,
            is_extra=False,
            created_by=generation_data.created_by
        )

        session.add(lesson)

        await session.flush()

        created_lesson_ids.append(
            lesson.id
        )

    return LessonGenerationResponse(
        template_id=template.id,
        date_from=generation_data.date_from,
        date_to=generation_data.date_to,
        created_count=len(created_lesson_ids),
        skipped_count=len(conflicts),
        created_lesson_ids=created_lesson_ids,
        conflicts=conflicts
    )