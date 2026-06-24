from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from user_service.db.session import get_db
from user_service.services.user_service import UserService

from user_service.schemas.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UserRoleUpdate
)


router = APIRouter(prefix="/users", tags=["Users"])


# @router.post(
#     "/",
#     response_model=UserResponse,
#     status_code=status.HTTP_201_CREATED,
#     summary="Создание пользователя",
#     description="""
# Создание нового пользователя.
#
# Используется:
# - auth-service после регистрации
# - admin-service для создания аккаунтов
#
# По умолчанию пользователь получает роль USER.
# """,
#     response_description="Созданный пользователь"
# )
# async def create_user(
#     data: UserCreate,
#     db: AsyncSession = Depends(get_db)
# ):
#
#     service = UserService(db)
#
#     try:
#         return await service.create_user(data)
#
#     except ValueError as e:
#         raise HTTPException(
#             status_code=400,
#             detail=str(e)
#         )



@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить пользователя",
    description="""
Получение информации о пользователе по ID.

Доступ:
- admin
- teacher (ограниченно)
- сам пользователь
""",
    response_description="Данные пользователя"
)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):

    service = UserService(db)

    user = await service.get_user(user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user



@router.get(
    "/",
    response_model=list[UserResponse],
    summary="Получить список пользователей",
    description="""
Получение списка пользователей.

Используется:
- административная панель
- управление пользователями

Поддерживает пагинацию.
""",
    response_description="Список пользователей"
)
async def get_users(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):

    service = UserService(db)

    return await service.get_users(
        limit,
        offset
    )



@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Обновление профиля пользователя",
    description="""
Изменение данных пользователя:

- имя
- фамилия
- email
- дата рождения
- аватар
""",
    response_description="Обновленный пользователь"
)
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db)
):

    service = UserService(db)

    try:

        return await service.update_user(
            user_id,
            data
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )



@router.patch(
    "/{user_id}/role",
    response_model=UserResponse,
    summary="Изменение роли пользователя",
    description="""
Изменение роли пользователя.

Только ADMIN.

Примеры:
USER → STUDENT
USER → TEACHER
USER → PARENT
""",
    response_description="Пользователь с новой ролью"
)
async def change_role(
    user_id: int,
    data: UserRoleUpdate,
    db: AsyncSession = Depends(get_db)
):

    service = UserService(db)


    try:

        return await service.change_role(
            user_id,
            data.role
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )



@router.patch(
    "/{user_id}/block",
    response_model=UserResponse,
    summary="Блокировка пользователя",
    description="""
Отключение аккаунта.

Пользователь:
- не может войти
- не получает события
- сохраняется в базе
""",
    response_description="Заблокированный пользователь"
)
async def block_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):

    service = UserService(db)


    try:

        return await service.block_user(
            user_id
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )



@router.patch(
    "/{user_id}/activate",
    response_model=UserResponse,
    summary="Активация пользователя",
    description="""
Восстановление заблокированного аккаунта.
""",
    response_description="Активный пользователь"
)
async def activate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):

    service = UserService(db)


    try:

        return await service.activate_user(
            user_id
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )



@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление пользователя",
    description="""
Удаление пользователя.

Операция только для ADMIN.
""",
)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):

    service = UserService(db)

    try:

        await service.delete_user(
            user_id
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.get(
    "/phone/{phone_number}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить пользователя по номеру телефона",
    description="""
Поиск пользователя по номеру телефона.

Используется:
- auth-service при авторизации
- восстановление доступа
- проверка существующего аккаунта

Возвращает полный профиль пользователя.
""",
    response_description="Данные пользователя",
    responses={
        404: {
            "description": "Пользователь с таким номером не найден"
        },
        422: {
            "description": "Некорректный формат номера телефона"
        }
    }
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