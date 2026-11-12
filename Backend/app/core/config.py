from functools import lru_cache
from typing import List, Union, Optional, Dict, Any
from pydantic import Field, field_validator, model_validator
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
    ENVIRONMENT: Optional[str] = None
    DEBUG: bool = True
    VERSION: str = "0.1.0"
    APP_BASE_URL: str = "http://localhost:3000"
    BASE_URL: str = "http://localhost:8000"

    API_V1_PREFIX: str = "/api/v1"

    # Database
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "certificate_platform"
    AUTO_INIT_INDEXES: bool = True

    # Security & JWT
    JWT_SECRET_KEY: str = "certiflow-local-dev-jwt-secret-key-must-be-long-and-secure-32chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Storage & Assets
    STORAGE_DIR: str = "storage"
    STORAGE_TYPE: str = "local"
    S3_ENDPOINT: Optional[str] = None
    S3_REGION: str = "auto"
    S3_BUCKET_NAME: Optional[str] = None
    S3_ACCESS_KEY_ID: Optional[str] = None
    S3_SECRET_ACCESS_KEY: Optional[str] = None
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

    # Email Delivery & Notification System (P6)
    EMAIL_PROVIDER: str = "mock"
    EMAIL_WORKER_CONCURRENCY: int = 5
    EMAIL_SEND_TIMEOUT: int = 30
    EMAIL_MAX_RETRIES: int = 3
    MAX_EMAIL_ATTACHMENT_SIZE_MB: int = 10
    ENCRYPTION_KEY: Optional[str] = None
    SIGNED_URL_SECRET: str = "certiflow-signed-download-url-secret-key-32chars!"
    SIGNED_URL_EXPIRY_HOURS: int = 24
    WEBHOOK_SIGNING_SECRET: str = "certiflow-webhook-signature-secret-key!"
    DEFAULT_SENDER_NAME: str = "CertiFlow"
    DEFAULT_SENDER_EMAIL: str = "certificates@certiflow.io"

    # Analytics & Reporting System (P7)
    ANALYTICS_CACHE_TTL_SECONDS: int = 60
    REPORT_EXPIRY_HOURS: int = 24
    MAX_REPORT_ROWS: int = 100000

    # Teams, RBAC, API Keys & Webhooks (P8)
    INVITATION_EXPIRY_DAYS: int = 7
    API_KEY_PREFIX_LIVE: str = "ck_live_"
    API_KEY_PREFIX_TEST: str = "ck_test_"
    API_KEY_DEFAULT_RATE_LIMIT_READ: int = 1000
    API_KEY_DEFAULT_RATE_LIMIT_WRITE: int = 100
    WEBHOOK_TIMEOUT_SECONDS: int = 10
    WEBHOOK_MAX_RETRIES: int = 5
    WEBHOOK_RETRY_BACKOFF_BASE: int = 60
    IDEMPOTENCY_TTL_SECONDS: int = 86400

    # Security, Performance & Production Hardening (P9)
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 15
    LOGIN_RATE_LIMIT_PER_MINUTE: int = 10
    MAX_UPLOAD_SIZE_MB: int = 50
    MAX_CSV_SIZE_MB: int = 50
    MAX_XLSX_SIZE_MB: int = 50
    MAX_IMAGE_SIZE_MB: int = 10
    MAX_PDF_SIZE_MB: int = 20
    MAX_ZIP_EXTRACT_FILES: int = 1000
    MAX_ZIP_EXTRACT_SIZE_MB: int = 100
    ENABLE_PROMETHEUS_METRICS: bool = True
    STUCK_JOB_TIMEOUT_SECONDS: int = 600
    HEARTBEAT_INTERVAL_SECONDS: int = 30
    BUILD_COMMIT: str = "certiflow-p10-prod"
    ENABLE_SECURITY_HEADERS: bool = True

    # Production Deployment, SaaS & Billing (P10)
    BILLING_PROVIDER: str = "mock"
    BILLING_SECRET_KEY: str = "sk_test_certiflow_mock_billing_secret_key_32c"
    BILLING_WEBHOOK_SECRET: str = "whsec_mock_billing_webhook_secret_key_32c"
    BILLING_CURRENCY: str = "INR"
    DEFAULT_TRIAL_DAYS: int = 14
    BILLING_GRACE_PERIOD_DAYS: int = 7
    BILLING_WARNING_THRESHOLDS: List[int] = [80, 90, 100]
    COST_PER_CERTIFICATE: float = 0.05
    COST_PER_EMAIL: float = 0.01
    COST_PER_GB_STORAGE_MONTHLY: float = 2.0

    # Open Badges, W3C Verifiable Credentials & Digital Credentials (P11)
    CREDENTIAL_ISSUER_DOMAIN: str = "https://certiflow.io"
    CREDENTIAL_SIGNING_ALGORITHM: str = "Ed25519"
    DEFAULT_CREDENTIAL_VALIDITY_DAYS: Optional[int] = None
    ENABLE_DIGITAL_CREDENTIALS: bool = True
    OPEN_BADGES_CONTEXT_URL: str = "https://w3id.org/openbadges/v3"
    W3C_VC_CONTEXT_URL: str = "https://www.w3.org/ns/credentials/v2"
    PUBLIC_CREDENTIAL_URL_PREFIX: str = "https://verify.certiflow.io/credentials"

    # Session, Cookie & CSRF Security (P13.1)
    COOKIE_ACCESS_NAME: str = "certiflow_access_token"
    COOKIE_REFRESH_NAME: str = "certiflow_refresh_token"
    COOKIE_CSRF_NAME: str = "certiflow_csrf_token"
    COOKIE_DOMAIN: Optional[str] = None
    COOKIE_SAMESITE: str = "lax"
    ALLOW_DEMO_AUTH: bool = False

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

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        """Fail startup immediately if production/staging uses default or insecure secrets — P12.04."""
        env = (self.ENVIRONMENT or self.APP_ENV or "").lower().strip()
        if self.STORAGE_TYPE.lower() not in ("local", "s3"):
            raise ValueError("STORAGE_TYPE must be either 'local' or 's3'.")
        if self.STORAGE_TYPE.lower() == "s3":
            missing_storage = [
                name for name, value in (
                    ("S3_BUCKET_NAME", self.S3_BUCKET_NAME),
                    ("S3_ACCESS_KEY_ID", self.S3_ACCESS_KEY_ID),
                    ("S3_SECRET_ACCESS_KEY", self.S3_SECRET_ACCESS_KEY),
                ) if not value
            ]
            if missing_storage:
                raise ValueError("S3 storage is enabled but required settings are missing: " + ", ".join(missing_storage))

        if env in ("production", "prod", "staging"):
            insecure_jwt_defaults = {
                "certiflow-local-dev-jwt-secret-key-must-be-long-and-secure-32chars",
                "secret",
                "changeme",
                "your-secret-key",
                "password",
            }
            if (
                self.JWT_SECRET_KEY in insecure_jwt_defaults
                or "local-dev" in self.JWT_SECRET_KEY
                or len(self.JWT_SECRET_KEY) < 32
            ):
                raise ValueError(
                    "CRITICAL PRODUCTION SECURITY ERROR: Insecure or default JWT_SECRET_KEY configured in production/staging. "
                    "Must be a cryptographically secure random secret at least 32 characters long."
                )

            if not self.ENCRYPTION_KEY:
                raise ValueError(
                    "CRITICAL PRODUCTION SECURITY ERROR: ENCRYPTION_KEY must be configured in production/staging."
                )

            if (
                self.SIGNED_URL_SECRET == "certiflow-signed-download-url-secret-key-32chars!"
                or len(self.SIGNED_URL_SECRET) < 16
            ):
                raise ValueError(
                    "CRITICAL PRODUCTION SECURITY ERROR: Insecure or default SIGNED_URL_SECRET configured in production/staging."
                )

            if (
                self.WEBHOOK_SIGNING_SECRET == "certiflow-webhook-signature-secret-key!"
                or len(self.WEBHOOK_SIGNING_SECRET) < 16
            ):
                raise ValueError(
                    "CRITICAL PRODUCTION SECURITY ERROR: Insecure or default WEBHOOK_SIGNING_SECRET configured in production/staging."
                )

            if self.BILLING_PROVIDER != "mock" and (
                "mock" in self.BILLING_SECRET_KEY or len(self.BILLING_SECRET_KEY) < 20
            ):
                raise ValueError(
                    "CRITICAL PRODUCTION SECURITY ERROR: Live billing provider configured without valid high-entropy BILLING_SECRET_KEY."
                )

            if env in ("production", "prod") and self.DEBUG:
                raise ValueError(
                    "CRITICAL PRODUCTION CONFIGURATION ERROR: DEBUG cannot be True in production environment."
                )

            if self.ALLOW_DEMO_AUTH:
                raise ValueError(
                    "CRITICAL PRODUCTION SECURITY ERROR: ALLOW_DEMO_AUTH must be False in production/staging environments — P13.1."
                )
        elif env in ("development", "test") and "ALLOW_DEMO_AUTH" not in self.model_fields_set:
            self.ALLOW_DEMO_AUTH = True

        return self


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
