from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = ""
    secret_key: str = ""
    algorithm: str = ""
    token_expire_time: float = 0
    valid_types: dict[str, str] = {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",  # noqa
        "application/pdf": ".pdf",
        "image/png": ".png",
        "image/jpeg": ".jpg",
    }

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()
