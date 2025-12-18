from fastapi import HTTPException, status
from typing import Dict
from app.schemas.user import UserLoginRequest, UserResponse, LoginResponse
from app.utils.auth import verify_password, create_access_token
from app.database import supabase_admin
from datetime import timedelta
from app.config import get_settings

settings = get_settings()


async def authenticate_user(credentials: UserLoginRequest) -> LoginResponse:
    """Controller for user login"""
    # Find user by email
    result = supabase_admin.table("users").select("*").eq("email", credentials.email).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    user = result.data[0]
    
    # Verify password
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user["id"], "email": user["email"]},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    
    # Optional: Log login attempt
    try:
        supabase_admin.table("login_history").insert({
            "user_id": user["id"],
            "success": True
        }).execute()
    except:
        pass  # Don't fail login if logging fails
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            role=user["role"],
            teacher_id=user.get("teacher_id"),
            age=user["age"],
            gender=user["gender"],
            organization=user["organization"],
            profile_image=user["profile_image"],
            is_active=user["is_active"],
            is_verified=user["is_verified"]
        )
    )


async def request_password_reset(email: str) -> Dict[str, str]:
    """Controller for password reset request"""
    from app.utils.token import generate_reset_token, get_token_expiry
    
    # Find user by email
    result = supabase_admin.table("users").select("id, email").eq("email", email).execute()
    
    # Don't reveal if email exists or not (security best practice)
    if not result.data:
        return {
            "message": "If the email exists, a password reset link has been sent",
            "success": True
        }
    
    user = result.data[0]
    
    # Generate reset token
    reset_token = generate_reset_token()
    token_expiry = get_token_expiry(hours=24)  # Token valid for 24 hours
    
    # Save reset token to database
    supabase_admin.table("password_reset_tokens").insert({
        "user_id": user["id"],
        "token": reset_token,
        "expires_at": token_expiry.isoformat()
    }).execute()
    
    # TODO: In production, send email with reset link containing the token
    # Example: https://yourapp.com/reset-password?token={reset_token}
    
    return {
        "message": "If the email exists, a password reset link has been sent",
        "success": True
    }


async def logout_user(user_id: str) -> Dict[str, str]:
    """Controller for user logout"""
    # Log the logout event (optional)
    try:
        supabase_admin.table("login_history").insert({
            "user_id": user_id,
            "success": True,
            # You could add a logout flag or separate logout table if needed
        }).execute()
    except:
        pass  # Don't fail logout if logging fails
    
    # With JWT tokens, logout is handled client-side by removing the token
    # Server-side logout would require a token blacklist/revocation system
    return {
        "message": "Successfully logged out",
        "success": True
    }
