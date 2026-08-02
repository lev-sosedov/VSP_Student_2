from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from common.security.dependencies import get_current_principal
from common.security.principal import CurrentPrincipal
from auth_service.schemas.schemas_auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    ChangePasswordRequest,
    ChangePasswordResponse
)

from auth_service.services.services_auth import AuthService
from auth_service.db.db_session import get_db
from auth_service.repositories.repository_refresh_session import RefreshSessionRepository
from auth_service.services.rate_limit import enforce_auth_rate_limit


router = APIRouter(prefix="/auth", tags=["Auth"])


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
    data: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)

    try:
        return await service.register(data)

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from error


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
    data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    await enforce_auth_rate_limit(request, "login", data.phone_number)
    service = AuthService(db)

    try:
        return await service.login(data)

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from error


# CHANGE PASSWORD
@router.patch(
    "/change-password",
    response_model=ChangePasswordResponse,
    status_code=status.HTTP_200_OK,
    summary="Изменить пароль текущего пользователя",
    description=(
        "Проверяет текущий пароль и сохраняет новый пароль. "
        "Пользователь определяется по access token."
    ),
    responses={
        400: {
            "description": "Текущий пароль неверный или новый пароль совпадает со старым"
        },
        401: {
            "description": "Недействительный access token"
        },
        403: {
            "description": "Аккаунт заблокирован"
        }
    }
)
async def change_password(
    data: ChangePasswordRequest,
    current_user: CurrentPrincipal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)

    try:
        return await service.change_password(
            user_id=int(current_user.claims["auth_user_id"]),
            data=data
        )

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from error


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
    data: RefreshRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    await enforce_auth_rate_limit(request, "refresh")
    service = AuthService(db)

    try:
        return await service.refresh(data)

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from error


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
async def logout(
    _principal: CurrentPrincipal = Depends(get_current_principal),
):
    await enforce_auth_rate_limit(request, "register", data.phone_number)
    return {
        "message": "logout endpoint",
        "revoked": True,
    }


@router.post("/logout-all", status_code=status.HTTP_200_OK)
async def logout_all(
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
):
    await AuthService(db).logout_all(int(principal.claims["auth_user_id"]))
    return {"message": "All sessions revoked", "revoked": True}


@router.get("/sessions")
async def sessions(
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
):
    items = await RefreshSessionRepository(db).list_user(int(principal.claims["auth_user_id"]))
    return [{
        "id": item.id,
        "created_at": item.created_at,
        "expires_at": item.expires_at,
        "last_used_at": item.last_used_at,
        "revoked_at": item.revoked_at,
    } for item in items]


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: int,
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
):
    repo = RefreshSessionRepository(db)
    items = await repo.list_user(int(principal.claims["auth_user_id"]))
    session = next((item for item in items if item.id == session_id), None)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    await repo.revoke(session, "user_revoked")
    return {"message": "Session revoked", "revoked": True}


@router.get("/me")
async def me(
    user: CurrentPrincipal = Depends(get_current_principal)
):
    return {"user_id": user.user_id, "role": user.role.value}
