"""Password hashing and the configured shared RS256 implementation."""

from passlib.context import CryptContext

from auth_service.core.core_config import settings
from common.security.config import JWTVerificationConfig
from common.security.jwt_issuer import JWTIssuer, JWTIssuerConfig
from common.security.jwt_provider import JWTProvider


pwd_context = CryptContext(
    schemes=["bcrypt"],
    bcrypt__rounds=settings.BCRYPT_ROUNDS,
    deprecated="auto",
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_issuer() -> JWTIssuer:
    return JWTIssuer(JWTIssuerConfig(
        private_key=settings.private_key(),
        algorithm=settings.JWT_ALGORITHM,
        issuer=settings.JWT_ISSUER,
        audience=settings.JWT_AUDIENCE,
        access_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
    ))


def get_verifier() -> JWTProvider:
    return JWTProvider(JWTVerificationConfig(
        algorithm=settings.JWT_ALGORITHM,
        issuer=settings.JWT_ISSUER,
        audience=settings.JWT_AUDIENCE,
        public_key=settings.public_key(),
        clock_skew_seconds=settings.JWT_CLOCK_SKEW_SECONDS,
    ))
