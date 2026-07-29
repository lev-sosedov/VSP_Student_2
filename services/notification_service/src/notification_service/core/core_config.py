import os


class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        (
            "postgresql+asyncpg://postgres:postgres@"
            "localhost:5432/notification_db"
        )
    )

    SERVICE_HOST: str = os.getenv(
        "SERVICE_HOST",
        "0.0.0.0"
    )

    SERVICE_PORT: int = int(
        os.getenv(
            "SERVICE_PORT",
            "8005"
        )
    )

    ENVIRONMENT: str = os.getenv(
        "ENVIRONMENT",
        "development"
    )

    SMTP_HOST: str = os.getenv(
        "SMTP_HOST",
        "smtp.mail.ru"
    )

    SMTP_PORT: int = int(
        os.getenv(
            "SMTP_PORT",
            "465"
        )
    )

    SMTP_USER: str = os.getenv(
        "SMTP_USER",
        ""
    )

    SMTP_PASSWORD: str = os.getenv(
        "SMTP_PASSWORD",
        ""
    )

    CONTACT_RECEIVER_EMAIL: str = os.getenv(
        "CONTACT_RECEIVER_EMAIL",
        ""
    )

    SMTP_TIMEOUT_SECONDS: int = int(
        os.getenv(
            "SMTP_TIMEOUT_SECONDS",
            "20"
        )
    )


settings = Settings()
