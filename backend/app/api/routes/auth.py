"""Authentication routes."""

from datetime import datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_token, verify_password, hash_password
from app.models.user import User
from app.schemas import (
    UserCreate,
    UserResponse,
    UserLogin,
    Token,
    MessageResponse,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current user from Bearer token in Authorization header."""
    from app.core.security import decode_token

    try:
        payload = decode_token(credentials.credentials)
        user_id = UUID(payload.get("sub"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate, db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Register a new user.

    - **email**: User's email address
    - **password**: User's password (min 8 characters)
    - **full_name**: User's full name
    - **username**: Unique username
    """
    try:
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        result = await db.execute(
            select(User).where(User.username == user_data.username)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

        new_user = User(
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
            username=user_data.username,
            is_active=True,
            is_admin=False,
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return UserResponse.model_validate(new_user)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user",
        ) from e


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin, db: AsyncSession = Depends(get_db)
) -> Token:
    """
    Login user with email and password.

    Returns access and refresh tokens.
    """
    try:
        result = await db.execute(
            select(User).where(User.email == credentials.email)
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(
            credentials.password, user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive",
            )

        access_token_data = {
            "sub": str(user.id),
            "type": "access",
        }
        refresh_token_data = {
            "sub": str(user.id),
            "type": "refresh",
        }

        access_token = create_token(
            access_token_data,
            expires_delta=timedelta(minutes=30),
        )
        refresh_token = create_token(
            refresh_token_data,
            expires_delta=timedelta(days=7),
        )

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=30 * 60,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed",
        ) from e


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """Get current user information."""
    return UserResponse.model_validate(current_user)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token: str, db: AsyncSession = Depends(get_db)
) -> Token:
    """
    Refresh access token using a refresh token.

    Returns new access and refresh tokens.
    """
    from app.core.security import decode_token

    try:
        payload = decode_token(token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        user_id = UUID(payload.get("sub"))

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        access_token_data = {
            "sub": str(user.id),
            "type": "access",
        }
        refresh_token_data = {
            "sub": str(user.id),
            "type": "refresh",
        }

        access_token = create_token(
            access_token_data,
            expires_delta=timedelta(minutes=30),
        )
        new_refresh_token = create_token(
            refresh_token_data,
            expires_delta=timedelta(days=7),
        )

        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=30 * 60,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to refresh token",
        ) from e
