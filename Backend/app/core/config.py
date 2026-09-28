from functools import lru_cache
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    APP_NAME: str = "CertiFlow API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    VERSION: str = "0.1.0"
    APP_BASE_URL: str = "http://localhost:3000"

    API_V1_PREFIX: str = "/api/v1"

    # Database
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "certificate_platform"

    # Security & JWT
    JWT_SECRET_KEY: str = "certiflow-local-dev-jwt-secret-key-must-be-long-and-secure-32chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Storage & Assets
    STORAGE_DIR: str = "storage"
    MAX_ASSET_SIZE_MB: int = 15
    ALLOWED_IMAGE_TYPES: List[str] = ["image/png", "image/jpeg", "image/jpg", "image/svg+xml"]

    # Redis & Job Queue (P4)
    REDIS_URL: str = "redis://localhost:6379"
    MAX_ACTIVE_JOBS_PER_ORG: int = 2
    MAX_ITEM_ATTEMPTS: int = 3
    RENDER_TIMEOUT_SECONDS: int = 120
    ZIP_EXPIRY_HOURS: int = 24
    WORKER_CONCURRENCY: int = 4

    # Verification & Trust System (P5)
    RATE_LIMIT_PUBLIC_VERIFY_PER_MINUTE: int = 60
    VERIFICATION_CACHE_TTL_SECONDS: int = 300
    PUBLIC_DOWNLOAD_ENABLED: bool = True

    # CORS
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
