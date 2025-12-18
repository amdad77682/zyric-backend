from fastapi import HTTPException, status
from app.schemas.user import UserRegisterRequest, UserResponse
from app.utils.auth import hash_password
from app.database import supabase_admin


async def register_user(user_data: UserRegisterRequest) -> UserResponse:
    """Controller for user registration"""
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
