from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    JWT_ALGORITHM: str = "RS256"
    JWT_PRIVATE_KEY_PATH: str
    JWT_PUBLIC_KEY_PATH: str
    JWT_ISSUER: str = "vsp-auth-service"
    JWT_AUDIENCE: str = "vsp-student-api"
    JWT_CLOCK_SKEW_SECONDS: int = 30

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14

    # USER_SERVICE_URL: str
    DATABASE_URL: str

    BCRYPT_ROUNDS: int = 12

    def private_key(self) -> str:
        return Path(self.JWT_PRIVATE_KEY_PATH).read_text(encoding="utf-8")

    def public_key(self) -> str:
        return Path(self.JWT_PUBLIC_KEY_PATH).read_text(encoding="utf-8")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
