from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.user import UserResponse, TeacherListResponse
from app.controllers.user_controller import get_all_teachers, get_students_by_teacher

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("/teachers", response_model=TeacherListResponse)
async def list_teachers():
    """
    Get list of all teachers
    
    Returns a list of all users with role 'teacher'
    """
    try:
        return await get_all_teachers()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred fetching teachers: {str(e)}"
        )


@router.get("/teachers/{teacher_id}/students", response_model=List[UserResponse])
async def list_students_by_teacher(teacher_id: str):
    """
    Get all students for a specific teacher
    
    - **teacher_id**: UUID of the teacher
    """
    try:
        return await get_students_by_teacher(teacher_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred fetching students: {str(e)}"
        )
