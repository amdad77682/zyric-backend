from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from typing import List, Optional
from app.schemas.question import QuestionGenerationResponse
from app.controllers.question_controller import process_images_and_generate_questions

router = APIRouter(prefix="/api/v1", tags=["Questions"])


@router.post("/generate-questions", response_model=QuestionGenerationResponse)
async def generate_questions(
    images: List[UploadFile] = File(..., description="Multiple images (5 or more) containing text to generate questions from"),
    subject: str = Form(..., description="Subject name"),
    num_questions: Optional[int] = Form(10, description="Number of questions to generate (1-50)"),
    difficulty: Optional[str] = Form("medium", description="Difficulty level: easy, medium, hard"),
    question_types: Optional[str] = Form(
        "multiple_choice,short_answer,true_false",
        description="Comma-separated question types"
    )
):
    """
    Generate questions from multiple images using Gemini AI
    
    - **images**: Upload multiple images (JPEG, PNG, WEBP) - supports 5+ images
    - **subject**: Subject name for the questions
    - **num_questions**: Number of questions to generate (default: 10, max: 50)
    - **difficulty**: Question difficulty (easy, medium, hard)
    - **question_types**: Types of questions (comma-separated: multiple_choice, short_answer, true_false)
    
    **Note:** Images can contain text in Bangla (Bengali) and/or English
    
    **Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/generate-questions" \
      -F "images=@image1.jpg" \
      -F "images=@image2.jpg" \
      -F "images=@image3.jpg" \
      -F "subject=Physics" \
      -F "num_questions=15" \
      -F "difficulty=medium"
    ```
    """
    try:
        # Validate minimum images
        if len(images) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"At least 2 images are required. You provided {len(images)} image(s)."
            )
        
        # Parse question types
        types_list = [t.strip() for t in question_types.split(",")] if question_types else None
        
        # Validate question types
        valid_types = ["multiple_choice", "short_answer", "true_false"]
        if types_list:
            for qt in types_list:
                if qt not in valid_types:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid question type: {qt}. Valid types: {', '.join(valid_types)}"
                    )
        
        # Validate difficulty
        valid_difficulties = ["easy", "medium", "hard"]
        if difficulty not in valid_difficulties:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid difficulty: {difficulty}. Valid values: {', '.join(valid_difficulties)}"
            )
        
        # Process images and generate questions
        result = await process_images_and_generate_questions(
            images=images,
            subject=subject,
            num_questions=num_questions,
            difficulty=difficulty,
            question_types=types_list
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating questions: {str(e)}"
        )
