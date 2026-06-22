from fastapi import APIRouter, HTTPException, status

from auth_service.schemas.schemas_auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RefreshRequest
)

from auth_service.services.auth_service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


service = AuthService()



# REGISTER
@router.post(
    "/register",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя",
    description="""
Создание нового аккаунта.

Процесс:
- проверка данных
- создание пользователя
- назначение роли USER
- выдача токенов

Используется:
- мобильное приложение
- web клиент
""",
    response_description="Результат регистрации",
    responses={
        400: {
            "description": "Пользователь уже существует или ошибка данных"
        },
        422: {
            "description": "Ошибка валидации"
        }
    }
)
async def register(
    data: RegisterRequest
):

    try:

        return await service.register(data)

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )




# LOGIN
@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Авторизация пользователя",
    description="""
Вход пользователя в систему.

Проверяет:
- номер телефона/email
- пароль

Возвращает:
- access token
- refresh token
""",
    response_description="JWT токены пользователя",
    responses={
        401: {
            "description": "Неверный логин или пароль"
        },
        422: {
            "description": "Ошибка валидации"
        }
    }
)
async def login(
    data: LoginRequest
):

    try:

        return await service.login(data)

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )




# REFRESH TOKEN
@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновление токена",
    description="""
Получение нового access token.

Используется когда:
- access token истёк
- refresh token ещё действителен
""",
    response_description="Новая пара JWT токенов",
    responses={
        401: {
            "description": "Недействительный refresh token"
        }
    }
)
async def refresh(
    data: RefreshRequest
):

    try:

        return await service.refresh(data)

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )




# LOGOUT
@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Выход пользователя",
    description="""
Завершение сессии.

В будущем:
- добавить blacklist JWT
- удалить refresh token из Redis
""",
    response_description="Сообщение об успешном выходе",
    responses={
        200: {
            "description": "Пользователь вышел"
        }
    }
)
async def logout():

    return {
        "message": "logout endpoint"
    }