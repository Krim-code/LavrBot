from pydantic import SecretStr
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    API_BASE_URL: str = "http://localhost:8000"
    PUBLIC_BASE_URL: str = "http://lavrpro.ru"
    LOG_LEVEL: str = "INFO"
    REDIS_URL: str | None = None  # на будущее

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache
def get_settings() -> Settings:
    return Settings()
