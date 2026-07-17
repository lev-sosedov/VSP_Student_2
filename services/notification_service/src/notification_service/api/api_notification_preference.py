from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession

from notification_service.db.db_session import (
    get_session
)
from notification_service.schemas.schemas_notification_preference import (
    NotificationPreferenceCreate,
    NotificationPreferenceResetRequest,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate
)
from notification_service.services.service_notification_preference import (
    NotificationPreferenceService
)


router = APIRouter(
    prefix="/notification-preferences",
    tags=["Notification preferences"]
)


# =====================================================
# Создать настройки уведомлений
# =====================================================

@router.post(
    "",
    response_model=NotificationPreferenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать настройки уведомлений"
)
async def create_notification_preference_endpoint(
    preference_data: NotificationPreferenceCreate,
    session: AsyncSession = Depends(get_session)
):
    service = NotificationPreferenceService(
        session=session
    )

    try:
        return await service.create(
            preference_data=preference_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Получить настройки пользователя
# =====================================================

@router.get(
    "/{user_id}",
    response_model=NotificationPreferenceResponse,
    summary="Получить настройки уведомлений пользователя"
)
async def get_notification_preference_endpoint(
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    service = NotificationPreferenceService(
        session=session
    )

    preference = await service.get_or_create_default(
        user_id=user_id
    )

    return preference


# =====================================================
# Изменить настройки пользователя
# =====================================================

@router.patch(
    "/{user_id}",
    response_model=NotificationPreferenceResponse,
    summary="Изменить настройки уведомлений"
)
async def update_notification_preference_endpoint(
    user_id: int,
    preference_data: NotificationPreferenceUpdate,
    session: AsyncSession = Depends(get_session)
):
    service = NotificationPreferenceService(
        session=session
    )

    preference = await service.get_by_user_id(
        user_id=user_id
    )

    if preference is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Настройки уведомлений не найдены"
        )

    try:
        return await service.update(
            preference=preference,
            preference_data=preference_data
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error


# =====================================================
# Сбросить настройки пользователя
# =====================================================

@router.post(
    "/{user_id}/reset",
    response_model=NotificationPreferenceResponse,
    summary="Сбросить настройки уведомлений"
)
async def reset_notification_preference_endpoint(
    user_id: int,
    reset_data: NotificationPreferenceResetRequest,
    session: AsyncSession = Depends(get_session)
):
    service = NotificationPreferenceService(
        session=session
    )

    preference = await service.get_by_user_id(
        user_id=user_id
    )

    if preference is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Настройки уведомлений не найдены"
        )

    try:
        return await service.reset(
            preference=preference,
            requested_by=reset_data.requested_by
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error