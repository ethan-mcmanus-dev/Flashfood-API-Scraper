"""
Application configuration settings.

Loads environment variables and provides type-safe configuration access.
"""

import json
import logging
from typing import List, Any
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


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

    # CORS - Enhanced with flexible parsing
    BACKEND_CORS_ORIGINS: str | List[str] = "http://localhost:5173,http://localhost:3000"

    @field_validator('BACKEND_CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v: Any) -> List[str]:
        """
        Parse CORS origins from various formats (JSON, CSV, space-separated).
        
        Supports:
        - JSON array: '["http://localhost:5173","http://localhost:3000"]'
        - CSV format: 'http://localhost:5173,http://localhost:3000'
        - Space-separated: 'http://localhost:5173 http://localhost:3000'
        - Single value: 'http://localhost:5173'
        """
        if isinstance(v, list):
            return v
        
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            
            # Try JSON format first
            if v.startswith('[') and v.endswith(']'):
                try:
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed if item]
                except json.JSONDecodeError:
                    pass
            
            # Try comma-separated
            if ',' in v:
                return [item.strip() for item in v.split(',') if item.strip()]
            
            # Try space-separated
            if ' ' in v:
                return [item.strip() for item in v.split() if item.strip()]
            
            # Single value
            return [v]
        
        # Fallback to default
        logger.warning(f"Could not parse CORS origins: {v}, using defaults")
        return [
            "http://localhost:5173",
            "http://localhost:3000",
        ]

    # Email Configuration
    EMAIL_SERVICE: str = "gmail"  # Options: "resend", "gmail", "mailgun"
    
    # Gmail SMTP (free option)
    GMAIL_EMAIL: str | None = None
    GMAIL_APP_PASSWORD: str | None = None
    
    # Resend (requires domain verification)
    RESEND_API_KEY: str | None = None
    EMAIL_FROM: str = "onboarding@resend.dev"

    # Flashfood API
    FLASHFOOD_API_KEY: str = "wEqsr63WozvJwNV4XKPv"
    FLASHFOOD_BASE_URL: str = "https://app.shopper.flashfood.com/api/v1"
    FLASHFOOD_POLL_INTERVAL_SECONDS: int = 300  # 5 minutes for production

    # Supported cities with coordinates
    SUPPORTED_CITIES: dict = {
        "calgary": {"lat": 51.0447, "lon": -114.0719, "name": "Calgary"},
        "vancouver": {"lat": 49.2827, "lon": -123.1207, "name": "Vancouver"},
        "toronto": {"lat": 43.6532, "lon": -79.3832, "name": "Toronto"},
        "edmonton": {"lat": 53.5461, "lon": -113.4938, "name": "Edmonton"},
        "waterloo": {"lat": 43.4643, "lon": -80.5204, "name": "Waterloo/Kitchener"},
    }

    @model_validator(mode='after')
    def validate_configuration(self):
        """Validate complete configuration after parsing."""
        errors = []
        
        # Validate SECRET_KEY
        if not self.SECRET_KEY or len(self.SECRET_KEY) < 32:
            errors.append({
                "field": "SECRET_KEY",
                "error": "SECRET_KEY must be at least 32 characters long",
                "resolution": "Generate a secure key: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            })
        
        # Validate CORS origins format
        for origin in self.BACKEND_CORS_ORIGINS:
            if not origin.startswith(('http://', 'https://')):
                errors.append({
                    "field": "BACKEND_CORS_ORIGINS",
                    "error": f"Invalid CORS origin format: {origin}",
                    "resolution": "CORS origins must start with http:// or https://"
                })
        
        # Validate database configuration
        if not all([self.POSTGRES_USER, self.POSTGRES_PASSWORD, self.POSTGRES_DB]):
            errors.append({
                "field": "DATABASE",
                "error": "Missing required database configuration",
                "resolution": "Set POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB environment variables"
            })
        
        if errors:
            error_details = "\n".join([f"- {err['field']}: {err['error']} ({err['resolution']})" for err in errors])
            logger.error(f"Configuration validation failed:\n{error_details}")
            raise ValueError(f"Configuration validation failed:\n{error_details}")
        
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Global settings instance
settings = Settings()
