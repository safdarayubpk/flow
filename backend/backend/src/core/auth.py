from fastapi import Request, Response, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from typing import Optional
from datetime import timedelta
from src.core.security import verify_token, create_access_token
from src.models.user import User
from src.core.database import get_session
from src.core.config import settings
from sqlmodel import Session, select


# Security scheme for JWT
security_scheme = HTTPBearer()


def create_auth_response(response: Response, access_token: str, refresh_token: str = None) -> None:
    """
    Create a response with JWT tokens stored in httpOnly cookies.
    This follows ADR-001 for secure JWT token storage.
    """
    # For cross-origin requests (frontend on different domain than backend):
    # - SameSite must be "none" to allow cross-origin cookies
    # - Secure must be True (required when SameSite=None)
    # In development with same origin, use "lax"
    is_cross_origin = settings.is_production or "vercel" in settings.cors_origins.lower()

    if is_cross_origin:
        samesite_policy = "none"
        is_secure = True
    else:
        samesite_policy = "lax"
        is_secure = False

    # Set access token in httpOnly cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=is_secure,
        samesite=samesite_policy,
        max_age=1800,  # 30 minutes
        path="/"
    )

    # Set refresh token in httpOnly cookie if provided
    if refresh_token:
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=is_secure,
            samesite=samesite_policy,
            max_age=int(timedelta(days=7).total_seconds()),  # 7 days
            path="/"
        )


def get_current_user(request: Request, session: Session = Depends(get_session)) -> User:
    """
    Get the current user from JWT token.
    Supports both:
    1. Authorization header (for cross-origin/localStorage scenarios)
    2. httpOnly cookie (for same-origin scenarios)
    """
    token_str = None

    # First, try to get token from Authorization header (cross-origin support)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token_str = auth_header[7:]

    # If no Authorization header, try httpOnly cookie
    if not token_str:
        token_str = request.cookies.get("access_token")
        if token_str and token_str.startswith("Bearer "):
            token_str = token_str[7:]

    if not token_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No access token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = verify_token(token_str)
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user from database
        user = session.exec(select(User).where(User.id == user_id)).first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except HTTPException:
        # Re-raise HTTP exceptions (like invalid credentials)
        raise
    except Exception as e:
        # Handle expired token and other JWT errors gracefully
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired or is invalid. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def logout_user(response: Response) -> Response:
    """
    Logout user by clearing the JWT tokens from httpOnly cookies.
    """
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    return response