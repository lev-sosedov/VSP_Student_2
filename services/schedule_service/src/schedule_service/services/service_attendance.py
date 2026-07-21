from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from common.utils.enum_attendance_status import (
    AttendanceStatus,
)
from schedule_service.models.model_attendance import (
    Attendance,
)
from schedule_service.models.model_lesson_schedule import (
    LessonSchedule,
)
from schedule_service.schemas.schemas_attendance import (
    AttendanceCreate,
    AttendanceUpdate,
)


async def get_attendance_by_id(
    session: AsyncSession,
    attendance_id: int,
) -> Attendance | None:
    query = select(Attendance).where(
        Attendance.id == attendance_id
    )

    result = await session.execute(query)

    return result.scalar_one_or_none()


async def get_attendance_by_lesson_and_student(
    session: AsyncSession,
    lesson_id: int,
    student_id: int,
) -> Attendance | None:
    query = select(Attendance).where(
        Attendance.lesson_id == lesson_id,
        Attendance.student_id == student_id,
    )

    result = await session.execute(query)

    return result.scalar_one_or_none()


async def get_attendance_records(
    session: AsyncSession,
    lesson_id: int | None = None,
    student_id: int | None = None,
    attendance_status: AttendanceStatus | None = None,
    marked_by: int | None = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Attendance], int]:
    filters = []

    if lesson_id is not None:
        filters.append(
            Attendance.lesson_id == lesson_id
        )

    if student_id is not None:
        filters.append(
            Attendance.student_id == student_id
        )

    if attendance_status is not None:
        filters.append(
            Attendance.status == attendance_status
        )

    if marked_by is not None:
        filters.append(
            Attendance.marked_by == marked_by
        )

    records_query = (
        select(Attendance)
        .where(*filters)
        .order_by(
            Attendance.lesson_id.desc(),
            Attendance.student_id,
            Attendance.id,
        )
        .offset(skip)
        .limit(limit)
    )

    count_query = (
        select(func.count(Attendance.id))
        .where(*filters)
    )

    records_result = await session.execute(
        records_query
    )

    count_result = await session.execute(
        count_query
    )

    records = list(
        records_result.scalars().all()
    )

    total = count_result.scalar_one()

    return records, total


async def create_attendance(
    session: AsyncSession,
    attendance_data: AttendanceCreate,
) -> Attendance:
    attendance = Attendance(
        lesson_id=attendance_data.lesson_id,
        student_id=attendance_data.student_id,
        status=attendance_data.status,
        late_minutes=attendance_data.late_minutes,
        comment=attendance_data.comment,
        marked_by=attendance_data.marked_by,
    )

    session.add(attendance)

    await session.flush()
    await session.refresh(attendance)

    return attendance


async def update_attendance(
    session: AsyncSession,
    attendance: Attendance,
    attendance_data: AttendanceUpdate,
) -> Attendance:
    update_data = attendance_data.model_dump(
        exclude_unset=True
    )

    marked_by = update_data.pop(
        "marked_by"
    )

    for field_name, field_value in update_data.items():
        setattr(
            attendance,
            field_name,
            field_value,
        )

    attendance.marked_by = marked_by

    if attendance.status != AttendanceStatus.LATE:
        attendance.late_minutes = 0

    await session.flush()
    await session.refresh(attendance)

    return attendance


async def get_lesson_for_attendance(
    session: AsyncSession,
    lesson_id: int,
) -> LessonSchedule | None:
    query = select(LessonSchedule).where(
        LessonSchedule.id == lesson_id
    )

    result = await session.execute(query)

    return result.scalar_one_or_none()