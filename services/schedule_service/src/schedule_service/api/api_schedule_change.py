from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession

from common.utils.enum_schedule_change_type import ScheduleChangeType
from schedule_service.db.db_session import get_session
from schedule_service.schemas.schemas_schedule_change import (
    ScheduleChangeListResponse,
    ScheduleChangeResponse
)
from schedule_service.services.service_schedule_change import (
    get_schedule_change_by_id,
    get_schedule_changes
)


router = APIRouter(
    prefix="/schedule-changes",
    tags=["Schedule changes"]
)


# =====================================================
# Получить список изменений расписания
# =====================================================

@router.get(
    "",
    response_model=ScheduleChangeListResponse,
    summary="Получить историю изменений расписания"
)
async def get_schedule_changes_endpoint(
    lesson_id: int | None = Query(
        default=None,
        gt=0
    ),
    changed_by: int | None = Query(
        default=None,
        gt=0
    ),
    change_type: ScheduleChangeType | None = Query(
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
    changes, total = await get_schedule_changes(
        session=session,
        lesson_id=lesson_id,
        changed_by=changed_by,
        change_type=change_type,
        skip=skip,
        limit=limit
    )

    return ScheduleChangeListResponse(
        total=total,
        items=changes
    )


# =====================================================
# Получить историю конкретного занятия
# Этот маршрут должен находиться раньше /{change_id}
# =====================================================

@router.get(
    "/lesson/{lesson_id}",
    response_model=ScheduleChangeListResponse,
    summary="Получить историю конкретного занятия"
)
async def get_lesson_schedule_changes_endpoint(
    lesson_id: int,
    session: AsyncSession = Depends(get_session)
):
    changes, total = await get_schedule_changes(
        session=session,
        lesson_id=lesson_id,
        skip=0,
        limit=500
    )

    return ScheduleChangeListResponse(
        total=total,
        items=changes
    )


# =====================================================
# Получить изменение по ID
# =====================================================

@router.get(
    "/{change_id}",
    response_model=ScheduleChangeResponse,
    summary="Получить запись об изменении по ID"
)
async def get_schedule_change_endpoint(
    change_id: int,
    session: AsyncSession = Depends(get_session)
):
    change = await get_schedule_change_by_id(
        session=session,
        change_id=change_id
    )

    if change is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись об изменении не найдена"
        )

    return change