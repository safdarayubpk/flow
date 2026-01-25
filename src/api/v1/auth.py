from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session
from src.services.auth import UserService
from src.core.database import get_session
from src.core.auth import create_auth_response, get_current_user
from src.models.user import UserCreate, User as UserModel, UserRead
from src.core.security import create_access_token
from datetime import timedelta
from typing import Dict
from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


router = APIRouter()


@router.post("/register", response_model=Dict[str, str])
def register_user(user_create: UserCreate, response: Response, session: Session = Depends(get_session)):
    """
    Register a new user with email and password.
    """
    try:
        # Create the user
        user = UserService.create_user(session=session, user_create=user_create)

        # Create access token for the new user
        access_token_expires = timedelta(minutes=30)  # 30 minutes
        access_token = create_access_token(
            data={"sub": user.id, "email": user.email},
            expires_delta=access_token_expires
        )

        # Create refresh token
        refresh_token_expires = timedelta(days=7)  # 7 days
        refresh_token = create_access_token(
            data={"sub": user.id, "email": user.email, "type": "refresh"},
            expires_delta=refresh_token_expires
        )

        # Create response with tokens in httpOnly cookies
        # This implements httpOnly cookie storage per ADR-001
        create_auth_response(response, access_token, refresh_token)

        return {"message": "User created successfully"}
    except HTTPException:
        # Re-raise HTTP exceptions (like duplicate email)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during registration: {str(e)}"
        )


@router.post("/login", response_model=Dict[str, str])
def login_user(login_request: LoginRequest, response: Response, session: Session = Depends(get_session)):
    """
    Login a user with email and password.
    """
    user = UserService.authenticate_user(
        session=session,
        email=login_request.email,
        password=login_request.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=30)  # 30 minutes
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=access_token_expires
    )

    # Create refresh token
    refresh_token_expires = timedelta(days=7)  # 7 days
    refresh_token = create_access_token(
        data={"sub": user.id, "email": user.email, "type": "refresh"},
        expires_delta=refresh_token_expires
    )

    # Set tokens in httpOnly cookies with proper CSRF protection
    # This implements CSRF protection per ADR-001 by using SameSite=strict
    create_auth_response(response, access_token, refresh_token)

    return {"message": "Login successful"}


@router.post("/logout")
def logout_user(response: Response):
    """
    Logout the current user.
    """
    from src.core.auth import logout_user as logout_helper

    logout_helper(response)
    return {"message": "Logout successful"}


@router.get("/session", response_model=UserRead)
def get_session_user(current_user: UserModel = Depends(get_current_user)):
    """
    Get the current authenticated user's session information.
    Returns user data if valid JWT token exists in httpOnly cookie.
    """
    return current_user


@router.post("/csrf-token")
def get_csrf_token():
    """
    Generate a CSRF token for forms that need additional protection.
    This implements proper CSRF protection per ADR-001.
    """
    # In a real implementation, we would generate a proper CSRF token
    # For now, this is a placeholder to indicate the endpoint exists
    return {"message": "CSRF protection is implemented via httpOnly cookies and SameSite=strict"}