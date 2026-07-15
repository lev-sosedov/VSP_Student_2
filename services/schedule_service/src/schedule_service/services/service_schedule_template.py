from datetime import time

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_service.models.model_room import Room
from schedule_service.models.model_schedule_template import (
    ScheduleTemplate
)
from schedule_service.schemas.schemas_schedule_template import (
    ScheduleTemplateCreate,
    ScheduleTemplateUpdate
)


# =====================================================
# Получение шаблона по ID
# =====================================================

async def get_schedule_template_by_id(
    session: AsyncSession,
    template_id: int
) -> ScheduleTemplate | None:
    query = select(ScheduleTemplate).where(
        ScheduleTemplate.id == template_id
    )

    result = await session.execute(query)

    return result.scalar_one_or_none()


# =====================================================
# Получение кабинета
# =====================================================

async def get_active_room_by_id(
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
# Получение списка шаблонов
# =====================================================

async def get_schedule_templates(
    session: AsyncSession,
    group_id: int | None = None,
    teacher_id: int | None = None,
    room_id: int | None = None,
    weekday: int | None = None,
    is_active: bool | None = None,
    skip: int = 0,
    limit: int = 100
) -> tuple[list[ScheduleTemplate], int]:
    filters = []

    if group_id is not None:
        filters.append(
            ScheduleTemplate.group_id == group_id
        )

    if teacher_id is not None:
        filters.append(
            ScheduleTemplate.teacher_id == teacher_id
        )

    if room_id is not None:
        filters.append(
            ScheduleTemplate.room_id == room_id
        )

    if weekday is not None:
        filters.append(
            ScheduleTemplate.weekday == weekday
        )

    if is_active is not None:
        filters.append(
            ScheduleTemplate.is_active == is_active
        )

    query = (
        select(ScheduleTemplate)
        .where(*filters)
        .order_by(
            ScheduleTemplate.weekday,
            ScheduleTemplate.start_time,
            ScheduleTemplate.group_id
        )
        .offset(skip)
        .limit(limit)
    )

    count_query = (
        select(func.count(ScheduleTemplate.id))
        .where(*filters)
    )

    result = await session.execute(query)
    count_result = await session.execute(count_query)

    templates = list(
        result.scalars().all()
    )

    total = count_result.scalar_one()

    return templates, total


# =====================================================
# Проверка пересечений
# =====================================================

async def find_schedule_conflict(
    session: AsyncSession,
    group_id: int,
    teacher_id: int,
    room_id: int,
    weekday: int,
    start_time: time,
    end_time: time,
    exclude_template_id: int | None = None
) -> ScheduleTemplate | None:
    """
    Пересечение существует, если:

    новое начало раньше окончания существующего занятия
    И
    новое окончание позже начала существующего занятия.
    """

    conflict_owner = or_(
        ScheduleTemplate.group_id == group_id,
        ScheduleTemplate.teacher_id == teacher_id,
        ScheduleTemplate.room_id == room_id
    )

    query = select(ScheduleTemplate).where(
        ScheduleTemplate.is_active.is_(True),
        ScheduleTemplate.weekday == weekday,
        ScheduleTemplate.start_time < end_time,
        ScheduleTemplate.end_time > start_time,
        conflict_owner
    )

    if exclude_template_id is not None:
        query = query.where(
            ScheduleTemplate.id != exclude_template_id
        )

    result = await session.execute(query)

    return result.scalars().first()


# =====================================================
# Создание шаблона
# =====================================================

async def create_schedule_template(
    session: AsyncSession,
    template_data: ScheduleTemplateCreate
) -> ScheduleTemplate:
    template = ScheduleTemplate(
        group_id=template_data.group_id,
        teacher_id=template_data.teacher_id,
        room_id=template_data.room_id,
        weekday=template_data.weekday,
        start_time=template_data.start_time,
        end_time=template_data.end_time,
        lesson_type=template_data.lesson_type
    )

    session.add(template)

    await session.flush()
    await session.refresh(template)

    return template


# =====================================================
# Изменение шаблона
# =====================================================

async def update_schedule_template(
    session: AsyncSession,
    template: ScheduleTemplate,
    template_data: ScheduleTemplateUpdate
) -> ScheduleTemplate:
    update_data = template_data.model_dump(
        exclude_unset=True
    )

    for field_name, field_value in update_data.items():
        setattr(
            template,
            field_name,
            field_value
        )

    await session.flush()
    await session.refresh(template)

    return template


# =====================================================
# Изменение активности шаблона
# =====================================================

async def set_schedule_template_activity(
    session: AsyncSession,
    template: ScheduleTemplate,
    is_active: bool
) -> ScheduleTemplate:
    template.is_active = is_active

    await session.flush()
    await session.refresh(template)

    return template