from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession

from common.utils.enum_notification_type import (
    NotificationType
)
from notification_service.db.db_session import (
    get_session
)
from notification_service.schemas.schemas_notification import (
    NotificationCreate,
    NotificationCreateResponse,
    NotificationReadAllResponse,
    NotificationReadRequest,
    NotificationReadResponse,
    NotificationUnreadCountResponse,
    UserNotificationListResponse,
    UserNotificationResponse
)
from notification_service.services.service_notification import (
    NotificationService
)


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


# =====================================================
# Создать уведомление
# =====================================================

@router.post(
    "",
    response_model=NotificationCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать уведомление"
)
async def create_notification_endpoint(
    notification_data: NotificationCreate,
    session: AsyncSession = Depends(get_session)
):
    service = NotificationService(
        session=session
    )

    try:
        notification, recipients = (
            await service.create(
                notification_data=notification_data
            )
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error

    return NotificationCreateResponse(
        id=notification.id,
        notification_type=(
            notification.notification_type
        ),
        priority=notification.priority,
        title=notification.title,
        message=notification.message,
        source_service=notification.source_service,
        event_type=notification.event_type,
        source_entity_type=(
            notification.source_entity_type
        ),
        source_entity_id=(
            notification.source_entity_id
        ),
        payload=notification.payload,
        created_at=notification.created_at,
        expires_at=notification.expires_at,
        recipients=recipients
    )


# =====================================================
# Получить уведомления пользователя
# =====================================================

@router.get(
    "/user/{user_id}",
    response_model=UserNotificationListResponse,
    summary="Получить уведомления пользователя"
)
async def get_user_notifications_endpoint(
    user_id: int,
    only_unread: bool | None = Query(
        default=None
    ),
    notification_type: (
        NotificationType | None
    ) = Query(
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
    service = NotificationService(
        session=session
    )

    items, total, unread_count = (
        await service.get_user_notifications(
            user_id=user_id,
            only_unread=only_unread,
            notification_type=notification_type,
            skip=skip,
            limit=limit
        )
    )

    return UserNotificationListResponse(
        total=total,
        unread_count=unread_count,
        items=items
    )


# =====================================================
# Счётчик непрочитанных
# Маршрут должен быть до динамического ID
# =====================================================

@router.get(
    "/user/{user_id}/unread-count",
    response_model=NotificationUnreadCountResponse,
    summary="Получить количество непрочитанных"
)
async def get_unread_count_endpoint(
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    service = NotificationService(
        session=session
    )

    unread_count = await service.get_unread_count(
        user_id=user_id
    )

    return NotificationUnreadCountResponse(
        user_id=user_id,
        unread_count=unread_count
    )


# =====================================================
# Прочитать все уведомления пользователя
# =====================================================

@router.post(
    "/user/{user_id}/read-all",
    response_model=NotificationReadAllResponse,
    summary="Отметить все уведомления прочитанными"
)
async def mark_all_notifications_as_read_endpoint(
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    service = NotificationService(
        session=session
    )

    updated_count = await service.mark_all_as_read(
        user_id=user_id
    )

    return NotificationReadAllResponse(
        user_id=user_id,
        updated_count=updated_count
    )


# =====================================================
# Получить конкретное уведомление пользователя
# =====================================================

@router.get(
    "/{notification_id}/user/{user_id}",
    response_model=UserNotificationResponse,
    summary="Получить уведомление пользователя"
)
async def get_user_notification_endpoint(
    notification_id: int,
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    service = NotificationService(
        session=session
    )

    notification = await service.get_user_notification(
        notification_id=notification_id,
        user_id=user_id
    )

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Уведомление пользователя не найдено"
        )

    return notification


# =====================================================
# Отметить уведомление прочитанным
# =====================================================

@router.post(
    "/{notification_id}/read",
    response_model=NotificationReadResponse,
    summary="Отметить уведомление прочитанным"
)
async def mark_notification_as_read_endpoint(
    notification_id: int,
    read_data: NotificationReadRequest,
    session: AsyncSession = Depends(get_session)
):
    service = NotificationService(
        session=session
    )

    try:
        recipient = await service.mark_as_read(
            notification_id=notification_id,
            user_id=read_data.user_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        ) from error

    return NotificationReadResponse(
        notification_id=notification_id,
        user_id=recipient.user_id,
        is_read=True,
        read_at=recipient.read_at
    )