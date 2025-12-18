from typing import List, Optional
from pydantic import BaseModel, Field


class QuestionGenerationRequest(BaseModel):
    """Schema for question generation request"""
    subject: str = Field(..., min_length=1, max_length=200, description="Subject name")
    num_questions: Optional[int] = Field(10, ge=1, le=50, description="Number of questions to generate")
    difficulty: Optional[str] = Field("medium", description="Difficulty level: easy, medium, hard")
    question_types: Optional[List[str]] = Field(
        ["multiple_choice", "short_answer", "true_false"],
        description="Types of questions to generate"
    )


class Question(BaseModel):
    """Schema for a single question"""
    question: str
    question_type: str
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    difficulty: str
    subject: str


class QuestionGenerationResponse(BaseModel):
    """Schema for question generation response"""
    success: bool
    subject: str
    total_questions: int
    questions: List[Question]
    extracted_text_preview: Optional[str] = None
