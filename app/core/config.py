from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Library Management API"
    database_url: str = "sqlite:///./library.db"
    fine_per_day: float = Field(default=1.0, ge=0)
    loan_period_days: int = Field(default=14, ge=1)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
