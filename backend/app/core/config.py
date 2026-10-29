import json
from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./zimhire.db"

    # Security
    SECRET_KEY: str = "development-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # File Upload
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_FILE_TYPES: list[str] = ["image/jpeg", "image/png", "image/gif"]
    UPLOAD_DIR: str = "uploads"

    @field_validator("CORS_ORIGINS", "ALLOWED_FILE_TYPES", mode="before")
    @classmethod
    def parse_list_fields(cls, value):
        if value is None:
            return []
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return []
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return parsed
            except (TypeError, ValueError):
                pass
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    # Payment
    PAYMENT_ADAPTER: str = "sandbox"  # sandbox or live
    ECOCASH_MERCHANT_CODE: Optional[str] = None
    ZIPIT_MERCHANT_CODE: Optional[str] = None

    # Timezone
    TIMEZONE: str = "Africa/Harare"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
