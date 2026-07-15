from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from schedule_service.models.model_room import Room
from schedule_service.schemas.schemas_room import (
    RoomCreate,
    RoomUpdate
)


# =====================================================
# Получение кабинета по ID
# =====================================================

async def get_room_by_id(
    session: AsyncSession,
    room_id: int
) -> Room | None:
    query = select(Room).where(
        Room.id == room_id
    )

    result = await session.execute(query)

    return result.scalar_one_or_none()


# =====================================================
# Поиск кабинета по названию внутри филиала
# =====================================================

async def get_room_by_name_and_branch(
    session: AsyncSession,
    branch_id: int,
    name: str
) -> Room | None:
    query = select(Room).where(
        Room.branch_id == branch_id,
        func.lower(Room.name) == name.strip().lower()
    )

    result = await session.execute(query)

    return result.scalar_one_or_none()


# =====================================================
# Создание кабинета
# =====================================================

async def create_room(
    session: AsyncSession,
    room_data: RoomCreate
) -> Room:
    room = Room(
        branch_id=room_data.branch_id,
        name=room_data.name,
        capacity=room_data.capacity,
        description=room_data.description
    )

    session.add(room)

    await session.flush()
    await session.refresh(room)

    return room


# =====================================================
# Получение списка кабинетов
# =====================================================

async def get_rooms(
    session: AsyncSession,
    branch_id: int | None = None,
    is_active: bool | None = None,
    skip: int = 0,
    limit: int = 100
) -> tuple[list[Room], int]:
    filters = []

    if branch_id is not None:
        filters.append(
            Room.branch_id == branch_id
        )

    if is_active is not None:
        filters.append(
            Room.is_active == is_active
        )

    rooms_query = (
        select(Room)
        .where(*filters)
        .order_by(
            Room.branch_id,
            Room.name,
            Room.id
        )
        .offset(skip)
        .limit(limit)
    )

    count_query = (
        select(func.count(Room.id))
        .where(*filters)
    )

    rooms_result = await session.execute(
        rooms_query
    )

    count_result = await session.execute(
        count_query
    )

    rooms = list(
        rooms_result.scalars().all()
    )

    total = count_result.scalar_one()

    return rooms, total


# =====================================================
# Изменение кабинета
# =====================================================

async def update_room(
    session: AsyncSession,
    room: Room,
    room_data: RoomUpdate
) -> Room:
    update_data = room_data.model_dump(
        exclude_unset=True
    )

    for field_name, field_value in update_data.items():
        setattr(
            room,
            field_name,
            field_value
        )

    await session.flush()
    await session.refresh(room)

    return room


# =====================================================
# Изменение активности кабинета
# =====================================================

async def set_room_activity(
    session: AsyncSession,
    room: Room,
    is_active: bool
) -> Room:
    room.is_active = is_active

    await session.flush()
    await session.refresh(room)

    return room