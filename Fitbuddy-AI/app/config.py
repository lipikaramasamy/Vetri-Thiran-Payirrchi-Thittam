from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str = "FitBuddy"

    DEBUG: bool = True

    DATABASE_URL: str = "sqlite:///./fitbuddy.db"

    GEMINI_API_KEY: str | None = None

    GEMINI_MODEL: str = "gemini-3.8-flash"

    ADMIN_KEY: str = "fitbuddy-admin-123"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:

    return Settings()


settings = get_settings()