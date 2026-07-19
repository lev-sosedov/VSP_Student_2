from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "VSP Student API Gateway"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8080
    APP_ENV: str = "development"
    DEBUG: bool = False

    AUTH_SERVICE_URL: str = "http://auth-service:8000"
    USER_SERVICE_URL: str = "http://user-service:8001"
    ACADEMIC_SERVICE_URL: str = "http://academic-service:8002"
    SCHEDULE_SERVICE_URL: str = "http://schedule-service:8003"
    CONTENT_SERVICE_URL: str = "http://content-service:8004"
    NOTIFICATION_SERVICE_URL: str = "http://notification-service:8005"
    COMMUNICATION_SERVICE_URL: str = "http://communication-service:8006"
    NEWS_SERVICE_URL: str = "http://news-service:8007"

    HTTP_CONNECT_TIMEOUT: float = Field(default=5.0, gt=0)
    HTTP_READ_TIMEOUT: float = Field(default=30.0, gt=0)

    CORS_ORIGINS: str = (
        "http://localhost:3000,"
        "http://localhost:5173"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]

    @property
    def service_urls(self) -> dict[str, str]:
        return {
            "auth": self.AUTH_SERVICE_URL,
            "users": self.USER_SERVICE_URL,
            "academic": self.ACADEMIC_SERVICE_URL,
            "schedule": self.SCHEDULE_SERVICE_URL,
            "content": self.CONTENT_SERVICE_URL,
            "notifications": self.NOTIFICATION_SERVICE_URL,
            "communication": self.COMMUNICATION_SERVICE_URL,
            "news": self.NEWS_SERVICE_URL,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()