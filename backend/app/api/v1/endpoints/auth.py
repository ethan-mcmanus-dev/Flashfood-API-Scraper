"""
Authentication endpoints for user registration and login.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.database import get_db
from app.models.user import User
from app.models.user_preference import UserPreference
from app.schemas.user import Token, UserCreate, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)) -> User:
    """
    Register a new user account.

    Creates user with hashed password and default preferences.

    Parameters:
        user_data: Registration information (email, password, name)
        db: Database session

    Returns:
        Created user object

    Raises:
        HTTPException: If email already registered
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=True,
        is_superuser=False,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Create default preferences for new user
    default_preferences = UserPreference(
        user_id=db_user.id,
        city="calgary",  # Default city
        max_distance_km=75.0,
        email_notifications=True,
        notify_new_deals=True,
        notify_price_drops=False,
        min_discount_percent=0,
        favorite_categories=[],
    )
    db.add(default_preferences)
    db.commit()

    return db_user


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> dict:
    """
    User login endpoint.

    Validates credentials and returns JWT access token.

    Parameters:
        form_data: OAuth2 form with username (email) and password
        db: Database session

    Returns:
        JWT access token

    Raises:
        HTTPException: If credentials are invalid
    """
    # Get user by email
    user = db.query(User).filter(User.email == form_data.username).first()

    # Verify credentials
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account",
        )

    # Create access token
    access_token = create_access_token(subject=user.email)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current user profile information.

    Parameters:
        current_user: Authenticated user from JWT token

    Returns:
        Current user profile
    """
    return current_user
