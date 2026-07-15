from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_service.db.db_session import get_session
from schedule_service.schemas.schemas_room import (
    RoomCreate,
    RoomListResponse,
    RoomResponse,
    RoomUpdate
)
from schedule_service.services.service_room import (
    create_room,
    get_room_by_id,
    get_room_by_name_and_branch,
    get_rooms,
    set_room_activity,
    update_room
)


router = APIRouter(
    prefix="/rooms",
    tags=["Rooms"]
)


# =====================================================
# Создание кабинета
# =====================================================

@router.post(
    "",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать кабинет"
)
async def create_room_endpoint(
    room_data: RoomCreate,
    session: AsyncSession = Depends(get_session)
):
    existing_room = await get_room_by_name_and_branch(
        session=session,
        branch_id=room_data.branch_id,
        name=room_data.name
    )

    if existing_room is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Кабинет с таким названием уже существует "
                "в указанном филиале"
            )
        )

    room = await create_room(
        session=session,
        room_data=room_data
    )

    return room


# =====================================================
# Получение списка кабинетов
# =====================================================

@router.get(
    "",
    response_model=RoomListResponse,
    summary="Получить список кабинетов"
)
async def get_rooms_endpoint(
    branch_id: int | None = Query(
        default=None,
        gt=0,
        description="Фильтр по ID филиала"
    ),
    is_active: bool | None = Query(
        default=None,
        description="Фильтр по активности кабинета"
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
    rooms, total = await get_rooms(
        session=session,
        branch_id=branch_id,
        is_active=is_active,
        skip=skip,
        limit=limit
    )

    return RoomListResponse(
        total=total,
        items=rooms
    )


# =====================================================
# Получение одного кабинета
# =====================================================

@router.get(
    "/{room_id}",
    response_model=RoomResponse,
    summary="Получить кабинет по ID"
)
async def get_room_endpoint(
    room_id: int,
    session: AsyncSession = Depends(get_session)
):
    room = await get_room_by_id(
        session=session,
        room_id=room_id
    )

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Кабинет не найден"
        )

    return room


# =====================================================
# Изменение кабинета
# =====================================================

@router.patch(
    "/{room_id}",
    response_model=RoomResponse,
    summary="Изменить кабинет"
)
async def update_room_endpoint(
    room_id: int,
    room_data: RoomUpdate,
    session: AsyncSession = Depends(get_session)
):
    room = await get_room_by_id(
        session=session,
        room_id=room_id
    )

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Кабинет не найден"
        )

    new_branch_id = (
        room_data.branch_id
        if room_data.branch_id is not None
        else room.branch_id
    )

    new_name = (
        room_data.name
        if room_data.name is not None
        else room.name
    )

    existing_room = await get_room_by_name_and_branch(
        session=session,
        branch_id=new_branch_id,
        name=new_name
    )

    if (
        existing_room is not None
        and existing_room.id != room.id
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Кабинет с таким названием уже существует "
                "в указанном филиале"
            )
        )

    updated_room = await update_room(
        session=session,
        room=room,
        room_data=room_data
    )

    return updated_room


# =====================================================
# Деактивация кабинета
# =====================================================

@router.post(
    "/{room_id}/deactivate",
    response_model=RoomResponse,
    summary="Деактивировать кабинет"
)
async def deactivate_room_endpoint(
    room_id: int,
    session: AsyncSession = Depends(get_session)
):
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
            detail="Кабинет уже деактивирован"
        )

    return await set_room_activity(
        session=session,
        room=room,
        is_active=False
    )


# =====================================================
# Активация кабинета
# =====================================================

@router.post(
    "/{room_id}/activate",
    response_model=RoomResponse,
    summary="Активировать кабинет"
)
async def activate_room_endpoint(
    room_id: int,
    session: AsyncSession = Depends(get_session)
):
    room = await get_room_by_id(
        session=session,
        room_id=room_id
    )

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Кабинет не найден"
        )

    if room.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Кабинет уже активен"
        )

    return await set_room_activity(
        session=session,
        room=room,
        is_active=True
    )