"""
Application configuration settings.

Loads environment variables and provides type-safe configuration access.
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All sensitive values should be stored in .env file or environment.
    """

    # Application
    PROJECT_NAME: str = "Flashfood Tracker"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "flashfood"

    @property
    def DATABASE_URL(self) -> str:
        """Construct PostgreSQL connection string."""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None

    @property
    def REDIS_URL(self) -> str:
        """Construct Redis connection string."""
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite default
        "http://localhost:3000",  # Alternative
    ]

    # Email (Resend)
    RESEND_API_KEY: str | None = None
    EMAIL_FROM: str = "notifications@flashfood-tracker.com"

    # Flashfood API
    FLASHFOOD_API_KEY: str = "wEqsr63WozvJwNV4XKPv"
    FLASHFOOD_BASE_URL: str = "https://app.shopper.flashfood.com/api/v1"
    FLASHFOOD_POLL_INTERVAL_SECONDS: int = 300  # 5 minutes

    # Supported cities with coordinates
    SUPPORTED_CITIES: dict = {
        "calgary": {"lat": 51.0447, "lon": -114.0719, "name": "Calgary"},
        "vancouver": {"lat": 49.2827, "lon": -123.1207, "name": "Vancouver"},
        "toronto": {"lat": 43.6532, "lon": -79.3832, "name": "Toronto"},
        "edmonton": {"lat": 53.5461, "lon": -113.4938, "name": "Edmonton"},
        "waterloo": {"lat": 43.4643, "lon": -80.5204, "name": "Waterloo/Kitchener"},
    }

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Global settings instance
settings = Settings()
