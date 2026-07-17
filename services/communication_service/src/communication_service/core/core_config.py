import os


class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        (
            "postgresql+asyncpg://postgres:postgres@"
            "localhost:5432/communication_db"
        )
    )

    SERVICE_HOST: str = os.getenv(
        "SERVICE_HOST",
        "0.0.0.0"
    )

    SERVICE_PORT: int = int(
        os.getenv(
            "SERVICE_PORT",
            "8006"
        )
    )

    ENVIRONMENT: str = os.getenv(
        "ENVIRONMENT",
        "development"
    )


settings = Settings()