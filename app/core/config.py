
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Palm Mind AI - RAG Backend"
    environment: str = "development"
    debug: bool = True

    database_url: str = (
        "postgresql+asyncpg://postgres:local_dev_password@localhost:5432/palm_mind"
    )
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection_name: str = "palm_mind_documents"

    gemini_api_key: SecretStr | None = None
    
    embedding_model: str = "gemini-embedding-001"
    embedding_dimension: int = 768
    llm_model: str = "gemini-3.1-flash-lite"

@lru_cache
def get_settings() -> Settings:
    return Settings()
