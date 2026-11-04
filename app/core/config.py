from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "CrediSure Dashboard API"
    Debug: bool = True
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    
    model_config = SettingsConfigDict(
        env_file=".env"
        env_file_encoding="utf-8"
        extra="ignore"
    )

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
