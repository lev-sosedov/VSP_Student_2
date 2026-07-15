from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from common.utils.enum_schedule_change_type import ScheduleChangeType
from schedule_service.models.model_schedule_change import ScheduleChange


# =====================================================
# Получить изменение по ID
# =====================================================

async def get_schedule_change_by_id(
    session: AsyncSession,
    change_id: int
) -> ScheduleChange | None:
    query = select(ScheduleChange).where(
        ScheduleChange.id == change_id
    )

    result = await session.execute(query)

    return result.scalar_one_or_none()


# =====================================================
# Получить список изменений
# =====================================================

async def get_schedule_changes(
    session: AsyncSession,
    lesson_id: int | None = None,
    changed_by: int | None = None,
    change_type: ScheduleChangeType | None = None,
    skip: int = 0,
    limit: int = 100
) -> tuple[list[ScheduleChange], int]:
    filters = []

    if lesson_id is not None:
        filters.append(
            ScheduleChange.lesson_id == lesson_id
        )

    if changed_by is not None:
        filters.append(
            ScheduleChange.changed_by == changed_by
        )

    if change_type is not None:
        filters.append(
            ScheduleChange.change_type == change_type
        )

    changes_query = (
        select(ScheduleChange)
        .where(*filters)
        .order_by(
            ScheduleChange.created_at.desc(),
            ScheduleChange.id.desc()
        )
        .offset(skip)
        .limit(limit)
    )

    count_query = (
        select(func.count(ScheduleChange.id))
        .where(*filters)
    )

    changes_result = await session.execute(
        changes_query
    )

    count_result = await session.execute(
        count_query
    )

    changes = list(
        changes_result.scalars().all()
    )

    total = count_result.scalar_one()

    return changes, total