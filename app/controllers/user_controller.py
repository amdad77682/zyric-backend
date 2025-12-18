from fastapi import HTTPException, status
from typing import List
from app.schemas.user import UserResponse, TeacherListResponse
from app.database import supabase_admin


async def get_all_teachers() -> TeacherListResponse:
    """Controller to get all teachers"""
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


async def get_students_by_teacher(teacher_id: str) -> List[UserResponse]:
    """Controller to get all students for a specific teacher"""
    # Verify teacher exists
    teacher = supabase_admin.table("users").select("id, role").eq("id", teacher_id).execute()
    
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
    
    # Query students for this teacher
    result = supabase_admin.table("users").select("*").eq("teacher_id", teacher_id).execute()
    
    # Convert to UserResponse objects
    students = []
    for user in result.data:
        students.append(UserResponse(
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
    
    return students
