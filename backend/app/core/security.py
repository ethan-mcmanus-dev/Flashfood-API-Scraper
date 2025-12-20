"""
Security utilities for authentication and authorization.

Handles password hashing, JWT token generation, and validation.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

logger = logging.getLogger(__name__)

def _create_password_context() -> CryptContext:
    """
    Create password hashing context with fallback strategies for bcrypt compatibility.
    
    Returns:
        CryptContext: Configured password context
        
    Raises:
        RuntimeError: If no compatible password hashing method can be initialized
    """
    try:
        # Primary: bcrypt with explicit configuration
        context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        # Test the context works
        test_hash = context.hash("test")
        context.verify("test", test_hash)
        logger.info("Password hashing initialized successfully with bcrypt")
        return context
    except Exception as e:
        logger.error(
            "Failed to initialize bcrypt password hashing",
            extra={
                "error": str(e),
                "resolution_steps": [
                    "Check bcrypt version compatibility (recommended: bcrypt==4.0.1)",
                    "Try downgrading to bcrypt==3.2.0 if issues persist",
                    "Consider switching to Argon2: pip install passlib[argon2]",
                    "Verify no conflicting bcrypt installations"
                ]
            }
        )
        raise RuntimeError(f"Password hashing initialization failed: {e}")

# Initialize password hashing context with error handling
pwd_context = _create_password_context()


def create_access_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    """
    Generate JWT access token.

    Parameters:
        subject: The subject (usually user ID) to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hash.

    Parameters:
        plain_password: The password to verify
        hashed_password: The stored password hash

    Returns:
        True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification failed: {e}")
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a password for secure storage.

    Parameters:
        password: Plain text password to hash

    Returns:
        Hashed password string
        
    Raises:
        ValueError: If password exceeds bcrypt 72-byte limit
    """
    # Validate password length (bcrypt limit is 72 bytes)
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        raise ValueError(
            f"Password is {len(password_bytes)} bytes, but bcrypt maximum is 72 bytes. "
            f"Consider truncating or using a different hashing algorithm."
        )
    
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Password hashing failed: {e}")
        raise RuntimeError(f"Failed to hash password: {e}")
