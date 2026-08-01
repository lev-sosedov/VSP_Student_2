import os


class Settings:
    DATABASE_URL: str = os.environ["DATABASE_URL"]


settings = Settings()
