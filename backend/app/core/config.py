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

    # Database - Railway provides DATABASE_URL directly
    DATABASE_URL: str | None = None
    
    # Fallback individual database settings for local development
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "flashfood"

    @property
    def get_database_url(self) -> str:
        """Get database URL - prefer Railway's DATABASE_URL, fallback to constructed URL."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        if not self.POSTGRES_USER or not self.POSTGRES_PASSWORD:
            raise ValueError("Either DATABASE_URL or POSTGRES_USER/POSTGRES_PASSWORD must be set")
            
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Redis - Railway provides REDIS_URL directly
    REDIS_URL: str | None = None
    
    # Fallback individual Redis settings for local development
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None

    @property
    def get_redis_url(self) -> str:
        """Get Redis URL - prefer Railway's REDIS_URL, fallback to constructed URL."""
        if self.REDIS_URL:
            return self.REDIS_URL
            
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
        missing_vars = []
        
        # Check for missing required environment variables
        if not self.SECRET_KEY:
            missing_vars.append("SECRET_KEY")
            
        # Check database configuration - either DATABASE_URL or individual settings
        if not self.DATABASE_URL and (not self.POSTGRES_USER or not self.POSTGRES_PASSWORD):
            missing_vars.extend(["DATABASE_URL or (POSTGRES_USER and POSTGRES_PASSWORD)"])
            
        if missing_vars:
            error_msg = f"""
RAILWAY DEPLOYMENT ERROR: Missing required environment variables: {', '.join(missing_vars)}

TO FIX THIS IN RAILWAY:
1. Go to your Railway project dashboard
2. Add PostgreSQL service: Click "New Service" → "Database" → "PostgreSQL"
3. Add Redis service: Click "New Service" → "Database" → "Redis"
4. Go to your backend service → "Variables" tab
5. Add these manual variables:
   - SECRET_KEY: Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
   - BACKEND_CORS_ORIGINS: *

Railway will automatically set DATABASE_URL and REDIS_URL when you add the database services.
"""
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Validate SECRET_KEY length
        if len(self.SECRET_KEY) < 32:
            logger.error("SECRET_KEY must be at least 32 characters long")
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        
        # Validate CORS origins format
        for origin in self.BACKEND_CORS_ORIGINS:
            # Allow wildcard for development/testing
            if origin == "*":
                continue
            if not origin.startswith(('http://', 'https://')):
                logger.error(f"Invalid CORS origin format: {origin}")
                raise ValueError(f"CORS origins must start with http:// or https:// (or use '*' for wildcard)")
        
        return self

    model_config = SettingsConfigDict(
        # Try .env file for local development, but don't fail if it doesn't exist
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        # Environment variables take precedence over .env file
        env_nested_delimiter="__",
    )


# Global settings instance
settings = Settings()
