from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "CrediSure Dashboard API"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "sqlite:///./credisure.db"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALLOW_DEMO_SEEDING: bool = False
    DEMO_USER_PASSWORD: str | None = None
    ADMIN_FULL_NAME: str | None = None
    ADMIN_EMAIL: str | None = None
    ADMIN_PASSWORD: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
