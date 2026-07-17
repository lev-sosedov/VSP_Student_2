from datetime import date, time
from enum import Enum as PythonEnum
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from common.utils.enum_lesson_status import LessonStatus
from common.utils.enum_schedule_change_type import ScheduleChangeType

from schedule_service.models.model_lesson_schedule import LessonSchedule
from schedule_service.models.model_room import Room
from schedule_service.models.model_schedule_change import ScheduleChange
from schedule_service.models.model_schedule_template import (
    ScheduleTemplate
)
from schedule_service.schemas.schemas_lesson_schedule import (
    LessonRescheduleRequest,
    LessonScheduleCreate,
    LessonScheduleUpdate
)
from schedule_service.messaging.messaging_event_publisher import (
    schedule_event_publisher
)


# =====================================================
# Получение занятия по ID
# =====================================================

async def get_lesson_by_id(
    session: AsyncSession,
    lesson_id: int
) -> LessonSchedule | None:
    query = select(LessonSchedule).where(
        LessonSchedule.id == lesson_id
    )

    result = await session.execute(query)

    return result.scalar_one_or_none()


# =====================================================
# Получение активного кабинета
# =====================================================

async def get_active_room(
    session: AsyncSession,
    room_id: int
) -> Room | None:
    query = select(Room).where(
        Room.id == room_id,
        Room.is_active.is_(True)
    )

    result = await session.execute(query)

    return result.scalar_one_or_none()


# =====================================================
# Получение активного шаблона
# =====================================================

async def get_active_template(
    session: AsyncSession,
    template_id: int
) -> ScheduleTemplate | None:
    query = select(ScheduleTemplate).where(
        ScheduleTemplate.id == template_id,
        ScheduleTemplate.is_active.is_(True)
    )

    result = await session.execute(query)

    return result.scalar_one_or_none()


# =====================================================
# Получение списка занятий
# =====================================================

async def get_lessons(
    session: AsyncSession,
    group_id: int | None = None,
    teacher_id: int | None = None,
    room_id: int | None = None,
    lesson_date_from: date | None = None,
    lesson_date_to: date | None = None,
    lesson_status: LessonStatus | None = None,
    is_extra: bool | None = None,
    skip: int = 0,
    limit: int = 100
) -> tuple[list[LessonSchedule], int]:
    filters = []

    if group_id is not None:
        filters.append(
            LessonSchedule.group_id == group_id
        )

    if teacher_id is not None:
        filters.append(
            LessonSchedule.teacher_id == teacher_id
        )

    if room_id is not None:
        filters.append(
            LessonSchedule.room_id == room_id
        )

    if lesson_date_from is not None:
        filters.append(
            LessonSchedule.lesson_date >= lesson_date_from
        )

    if lesson_date_to is not None:
        filters.append(
            LessonSchedule.lesson_date <= lesson_date_to
        )

    if lesson_status is not None:
        filters.append(
            LessonSchedule.status == lesson_status
        )

    if is_extra is not None:
        filters.append(
            LessonSchedule.is_extra == is_extra
        )

    lessons_query = (
        select(LessonSchedule)
        .where(*filters)
        .order_by(
            LessonSchedule.lesson_date,
            LessonSchedule.start_time,
            LessonSchedule.id
        )
        .offset(skip)
        .limit(limit)
    )

    count_query = (
        select(func.count(LessonSchedule.id))
        .where(*filters)
    )

    lessons_result = await session.execute(
        lessons_query
    )

    count_result = await session.execute(
        count_query
    )

    lessons = list(
        lessons_result.scalars().all()
    )

    total = count_result.scalar_one()

    return lessons, total


# =====================================================
# Проверка конфликта конкретных занятий
# =====================================================

async def find_lesson_conflict(
    session: AsyncSession,
    group_id: int,
    teacher_id: int,
    room_id: int,
    lesson_date: date,
    start_time: time,
    end_time: time,
    exclude_lesson_id: int | None = None
) -> LessonSchedule | None:
    conflict_owner = or_(
        LessonSchedule.group_id == group_id,
        LessonSchedule.teacher_id == teacher_id,
        LessonSchedule.room_id == room_id
    )

    query = select(LessonSchedule).where(
        LessonSchedule.lesson_date == lesson_date,

        LessonSchedule.status.in_([
            LessonStatus.SCHEDULED,
            LessonStatus.RESCHEDULED
        ]),

        LessonSchedule.start_time < end_time,
        LessonSchedule.end_time > start_time,

        conflict_owner
    )

    if exclude_lesson_id is not None:
        query = query.where(
            LessonSchedule.id != exclude_lesson_id
        )

    result = await session.execute(query)

    return result.scalars().first()


# =====================================================
# Создание занятия
# =====================================================

async def create_lesson(
    session: AsyncSession,
    lesson_data: LessonScheduleCreate
) -> LessonSchedule:
    lesson = LessonSchedule(
        group_id=lesson_data.group_id,
        teacher_id=lesson_data.teacher_id,
        room_id=lesson_data.room_id,
        template_id=lesson_data.template_id,
        lesson_date=lesson_data.lesson_date,
        start_time=lesson_data.start_time,
        end_time=lesson_data.end_time,
        status=LessonStatus.SCHEDULED,
        lesson_type=lesson_data.lesson_type,
        topic=lesson_data.topic,
        description=lesson_data.description,
        is_extra=lesson_data.is_extra,
        created_by=lesson_data.created_by
    )

    session.add(lesson)

    await session.flush()
    await session.refresh(lesson)

    await schedule_event_publisher.publish(
        routing_key="schedule.lesson.created",
        payload={
            "lesson_id": lesson.id,
            "group_id": lesson.group_id,
            "teacher_id": lesson.teacher_id,
            "room_id": lesson.room_id,
            "template_id": lesson.template_id,
            "lesson_date": lesson.lesson_date,
            "start_time": lesson.start_time,
            "end_time": lesson.end_time,
            "status": lesson.status,
            "lesson_type": lesson.lesson_type,
            "topic": lesson.topic,
            "description": lesson.description,
            "is_extra": lesson.is_extra,
            "created_by": lesson.created_by
        }
    )

    return lesson


# =====================================================
# Преобразование значений для JSON
# =====================================================

def serialize_value(value: Any) -> Any:
    if value is None:
        return None

    if isinstance(value, PythonEnum):
        return value.value

    if isinstance(value, (date, time)):
        return value.isoformat()

    return value


# =====================================================
# Создание снимка занятия
# =====================================================

def lesson_to_dict(
    lesson: LessonSchedule
) -> dict:
    return {
        "id": lesson.id,
        "group_id": lesson.group_id,
        "teacher_id": lesson.teacher_id,
        "room_id": lesson.room_id,
        "template_id": lesson.template_id,
        "lesson_date": serialize_value(
            lesson.lesson_date
        ),
        "start_time": serialize_value(
            lesson.start_time
        ),
        "end_time": serialize_value(
            lesson.end_time
        ),
        "status": serialize_value(
            lesson.status
        ),
        "lesson_type": serialize_value(
            lesson.lesson_type
        ),
        "topic": lesson.topic,
        "description": lesson.description,
        "is_extra": lesson.is_extra
    }


# =====================================================
# Запись истории изменения
# =====================================================

async def create_schedule_change(
    session: AsyncSession,
    lesson_id: int,
    change_type: ScheduleChangeType,
    old_data: dict | None,
    new_data: dict | None,
    changed_by: int,
    reason: str | None = None,
    comment: str | None = None
) -> ScheduleChange:
    schedule_change = ScheduleChange(
        lesson_id=lesson_id,
        change_type=change_type,
        old_data=old_data,
        new_data=new_data,
        reason=reason,
        changed_by=changed_by,
        comment=comment
    )

    session.add(schedule_change)

    await session.flush()
    await session.refresh(schedule_change)

    return schedule_change


# =====================================================
# Изменение занятия
# =====================================================

async def update_lesson(
    session: AsyncSession,
    lesson: LessonSchedule,
    lesson_data: LessonScheduleUpdate
) -> LessonSchedule:
    old_data = lesson_to_dict(
        lesson=lesson
    )

    update_data = lesson_data.model_dump(
        exclude_unset=True,
        exclude={
            "changed_by",
            "reason"
        }
    )

    for field_name, field_value in update_data.items():
        setattr(
            lesson,
            field_name,
            field_value
        )

    await session.flush()
    await session.refresh(lesson)

    new_data = lesson_to_dict(
        lesson=lesson
    )

    changed_by = lesson_data.changed_by

    # Замена преподавателя
    if (
        old_data["teacher_id"]
        != new_data["teacher_id"]
    ):
        await schedule_event_publisher.publish(
            routing_key=(
                "schedule.lesson.teacher_changed"
            ),
            payload={
                "lesson_id": lesson.id,
                "group_id": lesson.group_id,
                "old_teacher_id": (
                    old_data["teacher_id"]
                ),
                "new_teacher_id": (
                    new_data["teacher_id"]
                ),
                "lesson_date": lesson.lesson_date,
                "start_time": lesson.start_time,
                "end_time": lesson.end_time,
                "changed_by": changed_by,
                "reason": lesson_data.reason
            }
        )

    # Замена кабинета
    if old_data["room_id"] != new_data["room_id"]:
        await schedule_event_publisher.publish(
            routing_key=(
                "schedule.lesson.room_changed"
            ),
            payload={
                "lesson_id": lesson.id,
                "group_id": lesson.group_id,
                "teacher_id": lesson.teacher_id,
                "old_room_id": old_data["room_id"],
                "new_room_id": new_data["room_id"],
                "lesson_date": lesson.lesson_date,
                "start_time": lesson.start_time,
                "end_time": lesson.end_time,
                "changed_by": changed_by,
                "reason": lesson_data.reason
            }
        )

    await schedule_event_publisher.publish(
        routing_key="schedule.lesson.updated",
        payload={
            "lesson_id": lesson.id,
            "group_id": lesson.group_id,
            "teacher_id": lesson.teacher_id,
            "room_id": lesson.room_id,
            "lesson_date": lesson.lesson_date,
            "start_time": lesson.start_time,
            "end_time": lesson.end_time,
            "status": lesson.status,
            "old_data": old_data,
            "new_data": new_data,
            "changed_by": changed_by,
            "reason": lesson_data.reason
        }
    )

    return lesson


# =====================================================
# Изменение статуса занятия
# =====================================================

async def set_lesson_status(
    session: AsyncSession,
    lesson: LessonSchedule,
    lesson_status: LessonStatus
) -> LessonSchedule:
    old_status = lesson.status

    lesson.status = lesson_status

    await session.flush()
    await session.refresh(lesson)

    routing_keys = {
        LessonStatus.CANCELLED: (
            "schedule.lesson.cancelled"
        ),
        LessonStatus.COMPLETED: (
            "schedule.lesson.completed"
        ),
        LessonStatus.SCHEDULED: (
            "schedule.lesson.restored"
        )
    }

    routing_key = routing_keys.get(
        lesson_status,
        "schedule.lesson.status_changed"
    )

    await schedule_event_publisher.publish(
        routing_key=routing_key,
        payload={
            "lesson_id": lesson.id,
            "group_id": lesson.group_id,
            "teacher_id": lesson.teacher_id,
            "room_id": lesson.room_id,
            "lesson_date": lesson.lesson_date,
            "start_time": lesson.start_time,
            "end_time": lesson.end_time,
            "old_status": old_status,
            "new_status": lesson.status,
            "is_extra": lesson.is_extra
        }
    )

    return lesson


# =====================================================
# Перенос занятия
# =====================================================

async def reschedule_lesson(
    session: AsyncSession,
    lesson: LessonSchedule,
    reschedule_data: LessonRescheduleRequest
) -> LessonSchedule:
    old_data = lesson_to_dict(
        lesson=lesson
    )

    old_teacher_id = lesson.teacher_id
    old_room_id = lesson.room_id

    lesson.lesson_date = (
        reschedule_data.lesson_date
    )
    lesson.start_time = (
        reschedule_data.start_time
    )
    lesson.end_time = (
        reschedule_data.end_time
    )

    if reschedule_data.room_id is not None:
        lesson.room_id = reschedule_data.room_id

    if reschedule_data.teacher_id is not None:
        lesson.teacher_id = (
            reschedule_data.teacher_id
        )

    lesson.status = LessonStatus.RESCHEDULED

    await session.flush()
    await session.refresh(lesson)

    new_data = lesson_to_dict(
        lesson=lesson
    )

    await schedule_event_publisher.publish(
        routing_key="schedule.lesson.rescheduled",
        payload={
            "lesson_id": lesson.id,
            "group_id": lesson.group_id,

            "old_teacher_id": old_teacher_id,
            "new_teacher_id": lesson.teacher_id,

            "old_room_id": old_room_id,
            "new_room_id": lesson.room_id,

            "old_lesson_date": (
                old_data["lesson_date"]
            ),
            "new_lesson_date": (
                new_data["lesson_date"]
            ),

            "old_start_time": (
                old_data["start_time"]
            ),
            "new_start_time": (
                new_data["start_time"]
            ),

            "old_end_time": (
                old_data["end_time"]
            ),
            "new_end_time": (
                new_data["end_time"]
            ),

            "changed_by": (
                reschedule_data.changed_by
            ),
            "reason": reschedule_data.reason
        }
    )

    return lesson