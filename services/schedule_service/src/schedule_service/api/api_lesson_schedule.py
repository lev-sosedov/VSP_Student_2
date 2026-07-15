from datetime import date

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession

from common.utils.enum_lesson_status import LessonStatus
from common.utils.enum_schedule_change_type import ScheduleChangeType

from schedule_service.db.db_session import get_session
from schedule_service.models.model_lesson_schedule import LessonSchedule
from schedule_service.schemas.schemas_lesson_schedule import (
    LessonCancelRequest,
    LessonCompleteRequest,
    LessonRescheduleRequest,
    LessonScheduleCreate,
    LessonScheduleListResponse,
    LessonScheduleResponse,
    LessonScheduleUpdate
)
from schedule_service.services.service_lesson_schedule import (
    create_lesson,
    create_schedule_change,
    find_lesson_conflict,
    get_active_room,
    get_active_template,
    get_lesson_by_id,
    get_lessons,
    lesson_to_dict,
    reschedule_lesson,
    set_lesson_status,
    update_lesson
)


router = APIRouter(
    prefix="/lessons",
    tags=["Lessons"]
)


# =====================================================
# Текст ошибки конфликта
# =====================================================

def get_lesson_conflict_message(
    conflict: LessonSchedule,
    group_id: int,
    teacher_id: int,
    room_id: int
) -> str:
    conflict_reasons = []

    if conflict.group_id == group_id:
        conflict_reasons.append(
            "группа уже занята"
        )

    if conflict.teacher_id == teacher_id:
        conflict_reasons.append(
            "преподаватель уже занят"
        )

    if conflict.room_id == room_id:
        conflict_reasons.append(
            "кабинет уже занят"
        )

    reasons = ", ".join(conflict_reasons)

    return (
        f"Обнаружен конфликт занятия: {reasons}. "
        f"Конфликтующее занятие имеет ID {conflict.id}"
    )


# =====================================================
# Создание занятия
# =====================================================

@router.post(
    "",
    response_model=LessonScheduleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать конкретное занятие"
)
async def create_lesson_endpoint(
    lesson_data: LessonScheduleCreate,
    session: AsyncSession = Depends(get_session)
):
    room = await get_active_room(
        session=session,
        room_id=lesson_data.room_id
    )

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Активный кабинет не найден"
        )

    if lesson_data.template_id is not None:
        template = await get_active_template(
            session=session,
            template_id=lesson_data.template_id
        )

        if template is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Активный шаблон расписания не найден"
            )

        if template.group_id != lesson_data.group_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Указанная группа не соответствует "
                    "группе шаблона расписания"
                )
            )

    conflict = await find_lesson_conflict(
        session=session,
        group_id=lesson_data.group_id,
        teacher_id=lesson_data.teacher_id,
        room_id=lesson_data.room_id,
        lesson_date=lesson_data.lesson_date,
        start_time=lesson_data.start_time,
        end_time=lesson_data.end_time
    )

    if conflict is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=get_lesson_conflict_message(
                conflict=conflict,
                group_id=lesson_data.group_id,
                teacher_id=lesson_data.teacher_id,
                room_id=lesson_data.room_id
            )
        )

    return await create_lesson(
        session=session,
        lesson_data=lesson_data
    )


# =====================================================
# Получение списка занятий
# =====================================================

@router.get(
    "",
    response_model=LessonScheduleListResponse,
    summary="Получить список занятий"
)
async def get_lessons_endpoint(
    group_id: int | None = Query(
        default=None,
        gt=0
    ),
    teacher_id: int | None = Query(
        default=None,
        gt=0
    ),
    room_id: int | None = Query(
        default=None,
        gt=0
    ),
    lesson_date_from: date | None = Query(
        default=None
    ),
    lesson_date_to: date | None = Query(
        default=None
    ),
    lesson_status: LessonStatus | None = Query(
        default=None,
        alias="status"
    ),
    is_extra: bool | None = Query(
        default=None
    ),
    skip: int = Query(
        default=0,
        ge=0
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500
    ),
    session: AsyncSession = Depends(get_session)
):
    if (
        lesson_date_from is not None
        and lesson_date_to is not None
        and lesson_date_to < lesson_date_from
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "Конечная дата не может быть раньше начальной"
            )
        )

    lessons, total = await get_lessons(
        session=session,
        group_id=group_id,
        teacher_id=teacher_id,
        room_id=room_id,
        lesson_date_from=lesson_date_from,
        lesson_date_to=lesson_date_to,
        lesson_status=lesson_status,
        is_extra=is_extra,
        skip=skip,
        limit=limit
    )

    return LessonScheduleListResponse(
        total=total,
        items=lessons
    )


# =====================================================
# Получение занятий группы
# Важно: маршрут расположен до /{lesson_id}
# =====================================================

@router.get(
    "/group/{group_id}",
    response_model=LessonScheduleListResponse,
    summary="Получить занятия группы"
)
async def get_group_lessons_endpoint(
    group_id: int,
    lesson_date_from: date | None = Query(
        default=None
    ),
    lesson_date_to: date | None = Query(
        default=None
    ),
    session: AsyncSession = Depends(get_session)
):
    lessons, total = await get_lessons(
        session=session,
        group_id=group_id,
        lesson_date_from=lesson_date_from,
        lesson_date_to=lesson_date_to,
        skip=0,
        limit=500
    )

    return LessonScheduleListResponse(
        total=total,
        items=lessons
    )


# =====================================================
# Получение занятий преподавателя
# =====================================================

@router.get(
    "/teacher/{teacher_id}",
    response_model=LessonScheduleListResponse,
    summary="Получить занятия преподавателя"
)
async def get_teacher_lessons_endpoint(
    teacher_id: int,
    lesson_date_from: date | None = Query(
        default=None
    ),
    lesson_date_to: date | None = Query(
        default=None
    ),
    session: AsyncSession = Depends(get_session)
):
    lessons, total = await get_lessons(
        session=session,
        teacher_id=teacher_id,
        lesson_date_from=lesson_date_from,
        lesson_date_to=lesson_date_to,
        skip=0,
        limit=500
    )

    return LessonScheduleListResponse(
        total=total,
        items=lessons
    )


# =====================================================
# Получение занятия по ID
# =====================================================

@router.get(
    "/{lesson_id}",
    response_model=LessonScheduleResponse,
    summary="Получить занятие по ID"
)
async def get_lesson_endpoint(
    lesson_id: int,
    session: AsyncSession = Depends(get_session)
):
    lesson = await get_lesson_by_id(
        session=session,
        lesson_id=lesson_id
    )

    if lesson is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Занятие не найдено"
        )

    return lesson


# =====================================================
# Изменение занятия
# =====================================================

@router.patch(
    "/{lesson_id}",
    response_model=LessonScheduleResponse,
    summary="Изменить занятие"
)
async def update_lesson_endpoint(
    lesson_id: int,
    lesson_data: LessonScheduleUpdate,
    session: AsyncSession = Depends(get_session)
):
    lesson = await get_lesson_by_id(
        session=session,
        lesson_id=lesson_id
    )

    if lesson is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Занятие не найдено"
        )

    if lesson.status in {
        LessonStatus.CANCELLED,
        LessonStatus.COMPLETED
    }:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Нельзя изменить отменённое "
                "или завершённое занятие"
            )
        )

    new_group_id = (
        lesson_data.group_id
        if lesson_data.group_id is not None
        else lesson.group_id
    )

    new_teacher_id = (
        lesson_data.teacher_id
        if lesson_data.teacher_id is not None
        else lesson.teacher_id
    )

    new_room_id = (
        lesson_data.room_id
        if lesson_data.room_id is not None
        else lesson.room_id
    )

    new_lesson_date = (
        lesson_data.lesson_date
        if lesson_data.lesson_date is not None
        else lesson.lesson_date
    )

    new_start_time = (
        lesson_data.start_time
        if lesson_data.start_time is not None
        else lesson.start_time
    )

    new_end_time = (
        lesson_data.end_time
        if lesson_data.end_time is not None
        else lesson.end_time
    )

    if new_end_time <= new_start_time:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "Время окончания должно быть позже "
                "времени начала"
            )
        )

    room = await get_active_room(
        session=session,
        room_id=new_room_id
    )

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Активный кабинет не найден"
        )

    if lesson_data.template_id is not None:
        template = await get_active_template(
            session=session,
            template_id=lesson_data.template_id
        )

        if template is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Активный шаблон расписания не найден"
            )

    conflict = await find_lesson_conflict(
        session=session,
        group_id=new_group_id,
        teacher_id=new_teacher_id,
        room_id=new_room_id,
        lesson_date=new_lesson_date,
        start_time=new_start_time,
        end_time=new_end_time,
        exclude_lesson_id=lesson.id
    )

    if conflict is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=get_lesson_conflict_message(
                conflict=conflict,
                group_id=new_group_id,
                teacher_id=new_teacher_id,
                room_id=new_room_id
            )
        )

    old_data = lesson_to_dict(lesson)

    updated_lesson = await update_lesson(
        session=session,
        lesson=lesson,
        lesson_data=lesson_data
    )

    new_data = lesson_to_dict(updated_lesson)

    await create_schedule_change(
        session=session,
        lesson_id=lesson.id,
        change_type=ScheduleChangeType.UPDATED,
        old_data=old_data,
        new_data=new_data,
        changed_by=lesson_data.changed_by,
        reason=lesson_data.reason
    )

    return updated_lesson


# =====================================================
# Отмена занятия
# =====================================================

@router.post(
    "/{lesson_id}/cancel",
    response_model=LessonScheduleResponse,
    summary="Отменить занятие"
)
async def cancel_lesson_endpoint(
    lesson_id: int,
    cancel_data: LessonCancelRequest,
    session: AsyncSession = Depends(get_session)
):
    lesson = await get_lesson_by_id(
        session=session,
        lesson_id=lesson_id
    )

    if lesson is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Занятие не найдено"
        )

    if lesson.status == LessonStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Занятие уже отменено"
        )

    if lesson.status == LessonStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Нельзя отменить завершённое занятие"
        )

    old_data = lesson_to_dict(lesson)

    updated_lesson = await set_lesson_status(
        session=session,
        lesson=lesson,
        lesson_status=LessonStatus.CANCELLED
    )

    new_data = lesson_to_dict(updated_lesson)

    await create_schedule_change(
        session=session,
        lesson_id=lesson.id,
        change_type=ScheduleChangeType.CANCELLED,
        old_data=old_data,
        new_data=new_data,
        changed_by=cancel_data.changed_by,
        reason=cancel_data.reason
    )

    return updated_lesson


# =====================================================
# Завершение занятия
# =====================================================

@router.post(
    "/{lesson_id}/complete",
    response_model=LessonScheduleResponse,
    summary="Отметить занятие завершённым"
)
async def complete_lesson_endpoint(
    lesson_id: int,
    complete_data: LessonCompleteRequest,
    session: AsyncSession = Depends(get_session)
):
    lesson = await get_lesson_by_id(
        session=session,
        lesson_id=lesson_id
    )

    if lesson is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Занятие не найдено"
        )

    if lesson.status == LessonStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Занятие уже завершено"
        )

    if lesson.status == LessonStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Нельзя завершить отменённое занятие"
        )

    old_data = lesson_to_dict(lesson)

    updated_lesson = await set_lesson_status(
        session=session,
        lesson=lesson,
        lesson_status=LessonStatus.COMPLETED
    )

    new_data = lesson_to_dict(updated_lesson)

    await create_schedule_change(
        session=session,
        lesson_id=lesson.id,
        change_type=ScheduleChangeType.UPDATED,
        old_data=old_data,
        new_data=new_data,
        changed_by=complete_data.changed_by,
        reason=complete_data.reason,
        comment="Занятие отмечено завершённым"
    )

    return updated_lesson


# =====================================================
# Перенос занятия
# =====================================================

@router.post(
    "/{lesson_id}/reschedule",
    response_model=LessonScheduleResponse,
    summary="Перенести занятие"
)
async def reschedule_lesson_endpoint(
    lesson_id: int,
    reschedule_data: LessonRescheduleRequest,
    session: AsyncSession = Depends(get_session)
):
    lesson = await get_lesson_by_id(
        session=session,
        lesson_id=lesson_id
    )

    if lesson is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Занятие не найдено"
        )

    if lesson.status == LessonStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Нельзя перенести отменённое занятие"
        )

    if lesson.status == LessonStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Нельзя перенести завершённое занятие"
        )

    new_room_id = (
        reschedule_data.room_id
        if reschedule_data.room_id is not None
        else lesson.room_id
    )

    new_teacher_id = (
        reschedule_data.teacher_id
        if reschedule_data.teacher_id is not None
        else lesson.teacher_id
    )

    room = await get_active_room(
        session=session,
        room_id=new_room_id
    )

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Активный кабинет не найден"
        )

    conflict = await find_lesson_conflict(
        session=session,
        group_id=lesson.group_id,
        teacher_id=new_teacher_id,
        room_id=new_room_id,
        lesson_date=reschedule_data.lesson_date,
        start_time=reschedule_data.start_time,
        end_time=reschedule_data.end_time,
        exclude_lesson_id=lesson.id
    )

    if conflict is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=get_lesson_conflict_message(
                conflict=conflict,
                group_id=lesson.group_id,
                teacher_id=new_teacher_id,
                room_id=new_room_id
            )
        )

    old_data = lesson_to_dict(lesson)

    updated_lesson = await reschedule_lesson(
        session=session,
        lesson=lesson,
        reschedule_data=reschedule_data
    )

    new_data = lesson_to_dict(updated_lesson)

    await create_schedule_change(
        session=session,
        lesson_id=lesson.id,
        change_type=ScheduleChangeType.RESCHEDULED,
        old_data=old_data,
        new_data=new_data,
        changed_by=reschedule_data.changed_by,
        reason=reschedule_data.reason
    )

    return updated_lesson