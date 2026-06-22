from datetime import datetime, timedelta, timezone

from passlib.context import CryptContext
from jose import jwt, JWTError

from fastapi import HTTPException, status

from auth_service.core.core_config import settings


# PASSWORD HASH
pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=settings.BCRYPT_ROUNDS, deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


# JWT CREATE
def create_token(data: dict, expires_delta: timedelta, token_type: str):
    payload = data.copy()
    expire = (datetime.now(timezone.utc) + expires_delta)
    payload.update({"exp": int(expire.timestamp()), "type": token_type})

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


# ACCESS TOKEN
def create_access_token(data: dict):
    return create_token(data, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),"access")


# REFRESH TOKEN
def create_refresh_token(data: dict):
    return create_token(data, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS), "refresh")


# DECODE JWT
def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


# CHECK TOKEN TYPE
def verify_token_type(payload: dict, token_type: str):
    if payload.get("type") != token_type:
        raise HTTPException(status_code=401, detail="Wrong token type")
    return True


# функция декодирования JWT
# декодирует JWT
# проверяет подпись
# проверяет type == access
# возвращает payload или None

# def decode_token(token: str):
#     return jwt.decode(
#         token,
#         settings.JWT_SECRET_KEY,
#         algorithms=[settings.JWT_ALGORITHM]
#     )

def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        if payload.get("type") != "access":
            raise ValueError("Invalid token type")

        return payload

    except JWTError:
        return None