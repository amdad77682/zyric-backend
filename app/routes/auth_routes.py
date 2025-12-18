from fastapi import APIRouter, HTTPException, status, Depends, Header
from app.schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    ForgotPasswordRequest,
    UserResponse,
    LoginResponse,
    MessageResponse
)
from app.controllers.auth_controller import register_user
from app.controllers.login_controller import authenticate_user, request_password_reset, logout_user
from app.utils.auth import decode_access_token

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegisterRequest):
    """
    Register a new user
    
    - **email**: User's email address (must be unique)
    - **first_name**: User's first name
    - **last_name**: User's last name
    - **password**: User's password (min 8 chars, must contain uppercase and digit)
    - **role**: User role (teacher or student)
    - **teacher_id**: Required for students - UUID of the teacher
    - **age**: Optional user age
    - **gender**: Optional user gender
    - **organization**: Optional organization name
    - **profile_image**: Optional profile image URL
    """
    try:
        return await register_user(user_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during registration: {str(e)}"
        )


@router.post("/login", response_model=LoginResponse)
async def login(credentials: UserLoginRequest):
    """
    Login user and return access token
    
    - **email**: User's email address
    - **password**: User's password
    """
    try:
        return await authenticate_user(credentials)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during login: {str(e)}"
        )


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(request: ForgotPasswordRequest):
    """
    Request password reset token
    
    - **email**: User's email address
    
    Note: In a production environment, this should send an email with the reset token.
    For now, it creates the token in the database.
    """
    try:
        result = await request_password_reset(request.email)
        return MessageResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred processing your request: {str(e)}"
        )


@router.post("/logout", response_model=MessageResponse)
async def logout(authorization: str = Header(None)):
    """
    Logout user
    
    Requires Authorization header with Bearer token
    """
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )
        
        # Extract token
        token = authorization.replace("Bearer ", "")
        
        # Decode token to get user info
        payload = decode_access_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        user_id = payload.get("sub")
        
        # Call logout controller
        result = await logout_user(user_id)
        return MessageResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during logout: {str(e)}"
        )
