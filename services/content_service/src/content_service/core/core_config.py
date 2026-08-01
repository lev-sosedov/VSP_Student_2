import os


class Settings:
    DATABASE_URL: str = os.environ["DATABASE_URL"]

    SERVICE_HOST: str = os.getenv(
        "SERVICE_HOST",
        "0.0.0.0"
    )

    SERVICE_PORT: int = int(
        os.getenv(
            "SERVICE_PORT",
            "8004"
        )
    )


settings = Settings()
