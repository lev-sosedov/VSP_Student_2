from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_service.db.db_session import get_session
from schedule_service.models.model_schedule_template import (
    ScheduleTemplate
)
from schedule_service.schemas.schemas_schedule_template import (
    ScheduleTemplateCreate,
    ScheduleTemplateListResponse,
    ScheduleTemplateResponse,
    ScheduleTemplateUpdate
)
from schedule_service.services.service_external_validation import (
    validate_group_and_teacher,
    validate_room_branch
)
from schedule_service.services.service_room import (
    get_room_by_id
)
from schedule_service.services.service_schedule_template import (
    create_schedule_template,
    find_schedule_conflict,
    get_active_room_by_id,
    get_schedule_template_by_id,
    get_schedule_templates,
    set_schedule_template_activity,
    update_schedule_template
)


router = APIRouter(
    prefix="/schedule-templates",
    tags=["Schedule templates"]
)


# =====================================================
# Формирование сообщения о конфликте
# =====================================================

def get_conflict_message(
    conflict: ScheduleTemplate,
    group_id: int,
    teacher_id: int,
    room_id: int
) -> str:
    conflict_reasons: list[str] = []

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
        f"Обнаружен конфликт расписания: {reasons}. "
        f"Конфликтующий шаблон имеет ID {conflict.id}"
    )


# =====================================================
# Проверка группы, преподавателя и кабинета
# =====================================================

async def validate_template_relations(
    session: AsyncSession,
    group_id: int,
    teacher_id: int,
    room_id: int
) -> None:
    # Проверяем группу и преподавателя через RPC
    try:
        group, _teacher = await validate_group_and_teacher(
            group_id=group_id,
            teacher_id=teacher_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        ) from error

    # Получаем кабинет из schedule-service
    room = await get_room_by_id(
        session=session,
        room_id=room_id
    )

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Кабинет не найден"
        )

    if not room.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Кабинет неактивен"
        )

    # Проверяем, что кабинет находится
    # в том же филиале, что и группа
    try:
        validate_room_branch(
            room_branch_id=room.branch_id,
            group=group
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Создание шаблона
# =====================================================

@router.post(
    "",
    response_model=ScheduleTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать недельный шаблон расписания"
)
async def create_schedule_template_endpoint(
    template_data: ScheduleTemplateCreate,
    session: AsyncSession = Depends(get_session)
):
    await validate_template_relations(
        session=session,
        group_id=template_data.group_id,
        teacher_id=template_data.teacher_id,
        room_id=template_data.room_id
    )

    conflict = await find_schedule_conflict(
        session=session,
        group_id=template_data.group_id,
        teacher_id=template_data.teacher_id,
        room_id=template_data.room_id,
        weekday=template_data.weekday,
        start_time=template_data.start_time,
        end_time=template_data.end_time
    )

    if conflict is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=get_conflict_message(
                conflict=conflict,
                group_id=template_data.group_id,
                teacher_id=template_data.teacher_id,
                room_id=template_data.room_id
            )
        )

    template = await create_schedule_template(
        session=session,
        template_data=template_data
    )

    return template


# =====================================================
# Получение списка шаблонов
# =====================================================

@router.get(
    "",
    response_model=ScheduleTemplateListResponse,
    summary="Получить список шаблонов расписания"
)
async def get_schedule_templates_endpoint(
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
    weekday: int | None = Query(
        default=None,
        ge=0,
        le=6
    ),
    is_active: bool | None = Query(
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
    templates, total = await get_schedule_templates(
        session=session,
        group_id=group_id,
        teacher_id=teacher_id,
        room_id=room_id,
        weekday=weekday,
        is_active=is_active,
        skip=skip,
        limit=limit
    )

    return ScheduleTemplateListResponse(
        total=total,
        items=templates
    )


# =====================================================
# Получение шаблонов группы
# =====================================================

@router.get(
    "/group/{group_id}",
    response_model=ScheduleTemplateListResponse,
    summary="Получить расписание группы"
)
async def get_group_schedule_templates_endpoint(
    group_id: int,
    is_active: bool | None = Query(
        default=True
    ),
    session: AsyncSession = Depends(get_session)
):
    templates, total = await get_schedule_templates(
        session=session,
        group_id=group_id,
        is_active=is_active,
        skip=0,
        limit=500
    )

    return ScheduleTemplateListResponse(
        total=total,
        items=templates
    )


# =====================================================
# Получение одного шаблона
# =====================================================

@router.get(
    "/{template_id}",
    response_model=ScheduleTemplateResponse,
    summary="Получить шаблон расписания по ID"
)
async def get_schedule_template_endpoint(
    template_id: int,
    session: AsyncSession = Depends(get_session)
):
    template = await get_schedule_template_by_id(
        session=session,
        template_id=template_id
    )

    if template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Шаблон расписания не найден"
        )

    return template


# =====================================================
# Изменение шаблона
# =====================================================

@router.patch(
    "/{template_id}",
    response_model=ScheduleTemplateResponse,
    summary="Изменить шаблон расписания"
)
async def update_schedule_template_endpoint(
    template_id: int,
    template_data: ScheduleTemplateUpdate,
    session: AsyncSession = Depends(get_session)
):
    template = await get_schedule_template_by_id(
        session=session,
        template_id=template_id
    )

    if template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Шаблон расписания не найден"
        )

    new_group_id = (
        template_data.group_id
        if template_data.group_id is not None
        else template.group_id
    )

    new_teacher_id = (
        template_data.teacher_id
        if template_data.teacher_id is not None
        else template.teacher_id
    )

    new_room_id = (
        template_data.room_id
        if template_data.room_id is not None
        else template.room_id
    )

    new_weekday = (
        template_data.weekday
        if template_data.weekday is not None
        else template.weekday
    )

    new_start_time = (
        template_data.start_time
        if template_data.start_time is not None
        else template.start_time
    )

    new_end_time = (
        template_data.end_time
        if template_data.end_time is not None
        else template.end_time
    )

    new_is_active = (
        template_data.is_active
        if template_data.is_active is not None
        else template.is_active
    )

    if new_end_time <= new_start_time:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "Время окончания должно быть позже "
                "времени начала"
            )
        )

    # Проверяем связи только если итоговый шаблон активен.
    # Неактивный шаблон может временно хранить старые данные.
    if new_is_active:
        await validate_template_relations(
            session=session,
            group_id=new_group_id,
            teacher_id=new_teacher_id,
            room_id=new_room_id
        )

        conflict = await find_schedule_conflict(
            session=session,
            group_id=new_group_id,
            teacher_id=new_teacher_id,
            room_id=new_room_id,
            weekday=new_weekday,
            start_time=new_start_time,
            end_time=new_end_time,
            exclude_template_id=template.id
        )

        if conflict is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=get_conflict_message(
                    conflict=conflict,
                    group_id=new_group_id,
                    teacher_id=new_teacher_id,
                    room_id=new_room_id
                )
            )

    updated_template = await update_schedule_template(
        session=session,
        template=template,
        template_data=template_data
    )

    return updated_template


# =====================================================
# Деактивация шаблона
# =====================================================

@router.post(
    "/{template_id}/deactivate",
    response_model=ScheduleTemplateResponse,
    summary="Деактивировать шаблон расписания"
)
async def deactivate_schedule_template_endpoint(
    template_id: int,
    session: AsyncSession = Depends(get_session)
):
    template = await get_schedule_template_by_id(
        session=session,
        template_id=template_id
    )

    if template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Шаблон расписания не найден"
        )

    if not template.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Шаблон уже деактивирован"
        )

    return await set_schedule_template_activity(
        session=session,
        template=template,
        is_active=False
    )


# =====================================================
# Активация шаблона
# =====================================================

@router.post(
    "/{template_id}/activate",
    response_model=ScheduleTemplateResponse,
    summary="Активировать шаблон расписания"
)
async def activate_schedule_template_endpoint(
    template_id: int,
    session: AsyncSession = Depends(get_session)
):
    template = await get_schedule_template_by_id(
        session=session,
        template_id=template_id
    )

    if template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Шаблон расписания не найден"
        )

    if template.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Шаблон уже активен"
        )

    await validate_template_relations(
        session=session,
        group_id=template.group_id,
        teacher_id=template.teacher_id,
        room_id=template.room_id
    )

    conflict = await find_schedule_conflict(
        session=session,
        group_id=template.group_id,
        teacher_id=template.teacher_id,
        room_id=template.room_id,
        weekday=template.weekday,
        start_time=template.start_time,
        end_time=template.end_time,
        exclude_template_id=template.id
    )

    if conflict is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=get_conflict_message(
                conflict=conflict,
                group_id=template.group_id,
                teacher_id=template.teacher_id,
                room_id=template.room_id
            )
        )

    return await set_schedule_template_activity(
        session=session,
        template=template,
        is_active=True
    )