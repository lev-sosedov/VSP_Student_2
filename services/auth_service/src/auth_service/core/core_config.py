from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14

    USER_SERVICE_URL: str

    BCRYPT_ROUNDS: int = 12

    class Config:
        env_file = ".env"


settings = Settings()