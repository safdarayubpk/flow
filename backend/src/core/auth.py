from fastapi import Request, Response, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from typing import Optional
from datetime import timedelta
from src.core.security import verify_token, create_access_token
from src.models.user import User
from src.core.database import get_session
from sqlmodel import Session, select


# Security scheme for JWT
security_scheme = HTTPBearer()


def create_auth_response(response: Response, access_token: str, refresh_token: str = None) -> None:
    """
    Create a response with JWT tokens stored in httpOnly cookies.
    This follows ADR-001 for secure JWT token storage.
    """
    # Set access token in httpOnly cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=True,  # Set to True in production with HTTPS
        samesite="strict",  # Prevent CSRF attacks
        max_age=1800,  # 30 minutes
        path="/"
    )

    # Set refresh token in httpOnly cookie if provided
    if refresh_token:
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,  # Set to True in production with HTTPS
            samesite="strict",  # Prevent CSRF attacks
            max_age=timedelta(days=7).total_seconds(),  # 7 days
            path="/"
        )


def get_current_user(request: Request, session: Session = Depends(get_session)) -> User:
    """
    Get the current user from the JWT token in the httpOnly cookie.
    This follows ADR-001 for secure JWT token storage and handles expired tokens gracefully.
    """
    # Get token from httpOnly cookie
    token_str = request.cookies.get("access_token")

    if not token_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No access token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Remove "Bearer " prefix if present
    if token_str.startswith("Bearer "):
        token_str = token_str[7:]

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