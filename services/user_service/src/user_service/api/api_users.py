from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from common.security.permissions import require_admin, require_self_or_admin

from user_service.db.db_session import get_db
from user_service.services.service_user import UserService

from user_service.schemas.schemas_user import (
    PublicTeacherResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
    UserRoleUpdate
)


router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание пользователя",
)
async def create_user(
    data: UserCreate,
    _principal=Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)

    try:
        return await service.create_user(data)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.get(
    "/public/teachers",
    response_model=list[PublicTeacherResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить публичный список преподавателей",
    description=(
        "Возвращает только безопасные публичные поля "
        "активных пользователей с ролью TEACHER."
    ),
)
async def get_public_teachers(
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)

    return await service.get_public_teachers()


@router.get(
    "/phone/{phone_number}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить пользователя по номеру телефона",
)
async def get_user_by_phone(
    phone_number: str = Path(
        ...,
        title="Номер телефона",
        description="Номер телефона пользователя в международном формате",
        example="+79991234567",
        min_length=10,
        max_length=20
    ),
    _principal=Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)

    user = await service.get_user_by_phone(
        phone_number
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.get(
    "/",
    response_model=list[UserResponse],
    summary="Получить список пользователей",
)
async def get_users(
    limit: int = 20,
    offset: int = 0,
    _principal=Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)

    return await service.get_users(
        limit,
        offset
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить пользователя",
)
async def get_user(
    user_id: int,
    _principal=Depends(require_self_or_admin()),
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)

    user = await service.get_user(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Обновление профиля пользователя",
)
async def update_user(
    user_id: int,
    data: UserUpdate,
    _principal=Depends(require_self_or_admin()),
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)

    try:
        return await service.update_user(
            user_id,
            data
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )


@router.patch(
    "/{user_id}/role",
    response_model=UserResponse,
    summary="Изменение роли пользователя",
)
async def change_role(
    user_id: int,
    data: UserRoleUpdate,
    _principal=Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)

    try:
        return await service.change_role(
            user_id,
            data.role
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )


@router.patch(
    "/{user_id}/block",
    response_model=UserResponse,
    summary="Блокировка пользователя",
)
async def block_user(
    user_id: int,
    _principal=Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)

    try:
        return await service.block_user(
            user_id
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )


@router.patch(
    "/{user_id}/activate",
    response_model=UserResponse,
    summary="Активация пользователя",
)
async def activate_user(
    user_id: int,
    _principal=Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)

    try:
        return await service.activate_user(
            user_id
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )


@router.patch(
    "/{user_id}/verify-account",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Подтверждение аккаунта",
)
async def verify_account(
    user_id: int,
    _principal=Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)

    try:
        return await service.verify_account(
            user_id
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )


@router.patch(
    "/{user_id}/verify-phone",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Подтверждение телефона",
)
async def verify_phone(
    user_id: int,
    _principal=Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)

    try:
        return await service.verify_phone(
            user_id
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление пользователя",
)
async def delete_user(
    user_id: int,
    _principal=Depends(require_self_or_admin()),
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)

    try:
        await service.delete_user(
            user_id
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )
