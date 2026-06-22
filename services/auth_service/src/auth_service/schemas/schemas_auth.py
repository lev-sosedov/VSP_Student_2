from pydantic import BaseModel, Field
from typing import Optional


# Регистрация
class RegisterRequest(BaseModel):
    phone_number: str = Field(
        ...,
        example="+79991234567",
        description="Номер телефона пользователя"
    )

    password: str = Field(
        ...,
        min_length=8,
        example="Password123",
        description="Пароль пользователя"
    )

    user_name: Optional[str] = Field(
        default=None,
        example="Name",
        description="Имя пользователя"
    )


# Ответ
class RegisterResponse(BaseModel):
    user_id: int
    phone_number: str
    user_name: Optional[str]
    message: str = "User created successfully"


# Логин
class LoginRequest(BaseModel):

    phone_number: str = Field(
        ...,
        example="+79991234567"
    )

    password: str = Field(
        ...,
        example="StrongPassword123"
    )


# Токен
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str = Field(
        ...,
        description="Refresh JWT token"
    )