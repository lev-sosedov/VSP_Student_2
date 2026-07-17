from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)


class Settings(BaseSettings):
    database_url: str = (
        "postgresql+asyncpg://"
        "postgres:postgres@postgres:5432/news_db"
    )

    service_host: str = "0.0.0.0"
    service_port: int = 8007

    environment: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()