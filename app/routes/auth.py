from fastapi import APIRouter, HTTPException, status
from app.schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    ForgotPasswordRequest,
    UserResponse,
    LoginResponse,
    MessageResponse,
    TeacherListResponse
)
from app.utils.auth import hash_password, verify_password, create_access_token
from app.utils.token import generate_reset_token, get_token_expiry
from app.database import supabase_admin
from datetime import timedelta
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/api/v1", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegisterRequest):
    """
    Register a new user
    
    - **email**: User's email address (must be unique)
    - **first_name**: User's first name
    - **last_name**: User's last name
    - **password**: User's password (min 8 chars, must contain uppercase and digit)
    - **age**: Optional user age
    - **gender**: Optional user gender
    - **organization**: Optional organization name
    - **profile_image**: Optional profile image URL
    """
    try:
        # Check if user already exists
        existing_user = supabase_admin.table("users").select("*").eq("email", user_data.email).execute()
        
        if existing_user.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Validate teacher_id for students
        if user_data.role == "student":
            if not user_data.teacher_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Students must be associated with a teacher (teacher_id required)"
                )
            
            # Verify the teacher exists and is actually a teacher
            teacher = supabase_admin.table("users").select("id, role").eq("id", user_data.teacher_id).execute()
            
            if not teacher.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Teacher not found"
                )
            
            if teacher.data[0]["role"] != "teacher":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="The provided user is not a teacher"
                )
        
        # Teachers should not have a teacher_id
        if user_data.role == "teacher" and user_data.teacher_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Teachers cannot be associated with another teacher"
            )
        
        # Hash the password
        hashed_password = hash_password(user_data.password)
        
        # Prepare user data for insertion
        user_dict = {
            "email": user_data.email,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "password_hash": hashed_password,
            "role": user_data.role,
            "teacher_id": user_data.teacher_id if user_data.role == "student" else None,
            "age": user_data.age,
            "gender": user_data.gender,
            "organization": user_data.organization,
            "profile_image": user_data.profile_image,
        }
        
        # Insert user into database
        result = supabase_admin.table("users").insert(user_dict).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        # Return user data (without password hash)
        user = result.data[0]
        return UserResponse(
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
        # Find user by email
        result = supabase_admin.table("users").select("id, email").eq("email", request.email).execute()
        
        # Don't reveal if email exists or not (security best practice)
        if not result.data:
            return MessageResponse(
                message="If the email exists, a password reset link has been sent",
                success=True
            )
        
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
        # For now, we just create the token in the database
        
        return MessageResponse(
            message="If the email exists, a password reset link has been sent",
            success=True
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred processing your request: {str(e)}"
        )


@router.get("/teachers", response_model=TeacherListResponse)
async def get_teachers():
    """
    Get list of all teachers
    
    Returns a list of all users with role 'teacher'
    """
    try:
        # Query all teachers from database
        result = supabase_admin.table("users").select("*").eq("role", "teacher").execute()
        
        # Convert to UserResponse objects
        teachers = []
        for user in result.data:
            teachers.append(UserResponse(
                id=user["id"],
                email=user["email"],
                first_name=user["first_name"],
                last_name=user["last_name"],
                role=user["role"],
                teacher_id=user.get("teacher_id"),
                age=user.get("age"),
                gender=user.get("gender"),
                organization=user.get("organization"),
                profile_image=user.get("profile_image"),
                is_active=user["is_active"],
                is_verified=user["is_verified"]
            ))
        
        return TeacherListResponse(
            teachers=teachers,
            total=len(teachers)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred fetching teachers: {str(e)}"
        )
