from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "Sistema Documentale Aziendale"
    app_env: str = "development"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60

    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "document_management"

    solr_url: str = "http://localhost:8983/solr/documents"
    solr_timeout_seconds: int = 10

    storage_path: Path = Field(default=BASE_DIR / "storage")

    default_admin_username: str = "admin"
    default_admin_password: str = "Admin123!"

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.storage_path.mkdir(parents=True, exist_ok=True)
    return settings
