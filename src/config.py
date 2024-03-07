from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

TYPES = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/pdf": ".pdf",
    "image/png": ".png",
    "image/jpeg": ".jpg",
}


class Settings(BaseSettings):
    DATABASE_URL: str = ""
    SECRET_KEY: str = ""
    ALGORITHM: str = ""
    TOKEN_EXPIRE_TIME: float = 0
    VALID_TYPES: dict[str, str] = TYPES
    DB_HOST: str = ""
    DB_PORT: int = 0

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()
