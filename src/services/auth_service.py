"""
Authentication service for VoiceBridge API
Handles JWT token generation, validation, and user authentication
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from config import settings
from src.database.mysql_models import User, get_database_manager

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token scheme
security = HTTPBearer()


class AuthService:
    """Authentication service for handling JWT tokens and user authentication"""

    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        self.refresh_token_expire_days = settings.refresh_token_expire_days

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bool(pwd_context.verify(plain_password, hashed_password))

    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return str(pwd_context.hash(password))

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        # Ensure 'sub' field exists for JWT standard
        if "sub" not in to_encode and "id" in to_encode:
            to_encode["sub"] = str(to_encode["id"])
        elif "sub" not in to_encode:
            to_encode["sub"] = str(to_encode.get("username", "unknown"))

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return str(encoded_jwt)

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create a JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return str(encoded_jwt)

    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type. Expected {token_type}",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return dict(payload)
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password"""
        try:
            db_manager = get_database_manager()
            if not db_manager.connect():
                logger.error("Database connection failed")
                return None

            db = db_manager.get_session()
            user = db.query(User).filter(User.username == username).first()
            if not user:
                return None
            if not self.verify_password(password, user.password_hash):
                return None
            return user  # type: ignore
        except Exception as e:
            logger.error(f"Error authenticating user {username}: {e}")
            return None
        finally:
            if "db" in locals():
                db.close()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            db_manager = get_database_manager()
            if not db_manager.connect():
                logger.error("Database connection failed")
                return None

            db = db_manager.get_session()
            user = db.query(User).filter(User.id == user_id).first()
            return user  # type: ignore
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            return None
        finally:
            if "db" in locals():
                db.close()

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> Optional[User]:
        """Create a new user"""
        try:
            db_manager = get_database_manager()
            if not db_manager.connect():
                logger.error("Database connection failed")
                return None

            db = db_manager.get_session()

            # Check if user already exists
            existing_user = db.query(User).filter((User.username == username) | (User.email == email)).first()

            if existing_user:
                return None

            # Create new user
            hashed_password = self.get_password_hash(password)
            new_user = User(
                username=username,
                email=email,
                password_hash=hashed_password,
                first_name=first_name,
                last_name=last_name,
                is_active=True,
            )

            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            logger.info(f"Created new user: {username}")
            return new_user

        except Exception as e:
            logger.error(f"Error creating user {username}: {e}")
            if "db" in locals():
                db.rollback()
            return None
        finally:
            if "db" in locals():
                db.close()

    def update_user_last_login(self, user_id: int) -> None:
        """Update user's last login timestamp"""
        try:
            db_manager = get_database_manager()
            if not db_manager.connect():
                logger.error("Database connection failed")
                return

            db = db_manager.get_session()
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.updated_at = datetime.utcnow()
                db.commit()
        except Exception as e:
            logger.error(f"Error updating last login for user {user_id}: {e}")
        finally:
            if "db" in locals():
                db.close()


# Global auth service instance
auth_service = AuthService()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    payload = auth_service.verify_token(token, "access")

    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = auth_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


def create_tokens_for_user(user: User) -> Dict[str, str]:
    """Create access and refresh tokens for a user"""
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires,
    )

    refresh_token = auth_service.create_refresh_token(data={"sub": str(user.id), "username": user.username})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
