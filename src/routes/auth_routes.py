"""
Authentication routes for VoiceBridge API
Handles user registration, login, token refresh, and user management
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr

from config import settings
from src.database.mysql_models import User
from src.services.auth_service import auth_service, create_tokens_for_user, get_current_user
from src.services.rate_limiting_service import rate_limiting_service

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/auth", tags=["authentication"])


# Pydantic models for request/response
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    language_preference: str
    is_active: bool
    created_at: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


@router.post("/register", response_model=dict)
async def register_user(user_data: UserRegister, request: Request):
    """
    Register a new user account
    """
    # Apply rate limiting
    client_id = rate_limiting_service.get_client_identifier(request)
    await rate_limiting_service.enforce_rate_limit(client_id, "auth")

    try:
        # Validate password strength
        if len(user_data.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long",
            )

        # Create user
        user = auth_service.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists",
            )

        # Create tokens
        tokens = create_tokens_for_user(user)

        logger.info(f"New user registered: {user.username}")

        return {
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            **tokens,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/login", response_model=dict)
async def login_user(login_data: UserLogin, request: Request):
    """
    Authenticate user and return access tokens
    """
    # Apply rate limiting
    client_id = rate_limiting_service.get_client_identifier(request)
    await rate_limiting_service.enforce_rate_limit(client_id, "auth")

    try:
        # Authenticate user
        user = auth_service.authenticate_user(login_data.username, login_data.password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated",
            )

        # Update last login
        auth_service.update_user_last_login(user.id)

        # Create tokens
        tokens = create_tokens_for_user(user)

        logger.info(f"User logged in: {user.username}")

        return {
            "message": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "language_preference": user.language_preference,
            },
            **tokens,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_data: RefreshTokenRequest, request: Request):
    """
    Refresh access token using refresh token
    """
    # Apply rate limiting
    client_id = rate_limiting_service.get_client_identifier(request)
    await rate_limiting_service.enforce_rate_limit(client_id, "auth")

    try:
        # Verify refresh token
        payload = auth_service.verify_token(refresh_data.refresh_token, "refresh")
        user_id = int(payload.get("sub"))

        # Get user
        user = auth_service.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        # Create new tokens
        tokens = create_tokens_for_user(user)

        logger.info(f"Token refreshed for user: {user.username}")

        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=settings.access_token_expire_minutes * 60,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        language_preference=current_user.language_preference,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat(),
    )


@router.put("/me", response_model=UserResponse)
async def update_user_info(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    language_preference: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """
    Update current user information
    """
    try:
        from src.database.mysql_models import get_database_manager

        db_manager = get_database_manager()
        db = db_manager.get_session()

        # Update user fields
        if first_name is not None:
            current_user.first_name = first_name
        if last_name is not None:
            current_user.last_name = last_name
        if language_preference is not None:
            current_user.language_preference = language_preference

        db.commit()
        db.refresh(current_user)

        logger.info(f"User info updated: {current_user.username}")

        return UserResponse(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            language_preference=current_user.language_preference,
            is_active=current_user.is_active,
            created_at=current_user.created_at.isoformat(),
        )

    except Exception as e:
        logger.error(f"Error updating user info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
    finally:
        db.close()


@router.post("/change-password")
async def change_password(password_data: PasswordChangeRequest, current_user: User = Depends(get_current_user)):
    """
    Change user password
    """
    try:
        # Verify current password
        if not auth_service.verify_password(password_data.current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        # Validate new password
        if len(password_data.new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be at least 8 characters long",
            )

        # Update password
        from src.database.mysql_models import get_database_manager

        db_manager = get_database_manager()
        db = db_manager.get_session()

        current_user.password_hash = auth_service.get_password_hash(password_data.new_password)
        db.commit()

        logger.info(f"Password changed for user: {current_user.username}")

        return {"message": "Password changed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
    finally:
        db.close()


@router.post("/logout")
async def logout_user(current_user: User = Depends(get_current_user)):
    """
    Logout user (client should discard tokens)
    """
    # In a stateless JWT system, logout is handled client-side
    # We could implement a token blacklist here if needed
    logger.info(f"User logged out: {current_user.username}")

    return {"message": "Logged out successfully"}


@router.get("/rate-limit-status")
async def get_rate_limit_status(request: Request, current_user: Optional[User] = Depends(get_current_user)):
    """
    Get current rate limit status for the user
    """
    client_id = rate_limiting_service.get_client_identifier(request, current_user.id if current_user else None)

    status_info = {}
    for endpoint in ["transcription", "websocket", "auth", "general"]:
        status_info[endpoint] = rate_limiting_service.get_rate_limit_status(client_id, endpoint)

    return {"client_id": client_id, "rate_limits": status_info}
