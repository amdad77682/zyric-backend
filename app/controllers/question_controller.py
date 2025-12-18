import os
import base64
import json
import time
from typing import List
from io import BytesIO
from PIL import Image
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from fastapi import UploadFile, HTTPException, status
from app.config import get_settings
from app.schemas.question import Question, QuestionGenerationResponse

settings = get_settings()

# Configure Gemini
genai.configure(api_key=settings.google_api_key)


async def extract_text_from_images(images: List[UploadFile]) -> str:
    """
    Extract text from multiple images using Gemini Vision OCR
    Supports Bangla and English text
    """
    all_extracted_text = []
    
    # Initialize Gemini Vision model for OCR with timeout settings
    vision_model = genai.GenerativeModel('gemini-2.5-flash-lite')
    
    for idx, image_file in enumerate(images):
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                # Read image content
                image_content = await image_file.read()
                
                # Open image with PIL
                image = Image.open(BytesIO(image_content))
                
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Resize large images to reduce processing time
                max_size = 1024
                if max(image.size) > max_size:
                    ratio = max_size / max(image.size)
                    new_size = tuple(int(dim * ratio) for dim in image.size)
                    image = image.resize(new_size, Image.Resampling.LANCZOS)
                
                # Extract text using Gemini Vision with simpler prompt
                prompt = "Extract all text from this image. Include both Bangla and English text."
                
                response = vision_model.generate_content([prompt, image])
                extracted_text = response.text
                
                all_extracted_text.append(f"--- Image {idx + 1} ---\n{extracted_text}\n")
                
                # Reset file pointer for potential reuse
                await image_file.seek(0)
                
                # Success - break retry loop
                break
                
            except Exception as e:
                error_msg = str(e)
                
                # If timeout or 504, retry
                if ("timeout" in error_msg.lower() or "504" in error_msg) and attempt < max_retries - 1:
                    print(f"Attempt {attempt + 1} failed for image {idx + 1}, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    await image_file.seek(0)  # Reset file pointer for retry
                    continue
                
                # Final failure after retries
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error extracting text from image {idx + 1} after {max_retries} attempts: {error_msg}"
                )
    
    return "\n".join(all_extracted_text)


async def generate_questions_from_content(
    content: str,
    subject: str,
    num_questions: int = 10,
    difficulty: str = "medium",
    question_types: List[str] = None
) -> QuestionGenerationResponse:
    """
    Generate questions from extracted content using Gemini LLM
    """
    if question_types is None:
        question_types = ["multiple_choice", "short_answer", "true_false"]
    
    try:
        # Initialize Gemini LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            google_api_key=settings.google_api_key,
            temperature=0.7,
            convert_system_message_to_human=True
        )
        
        # Create prompt template
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert educator creating educational questions.
            Generate questions based on the provided content for the subject: {subject}.
            The content may be in Bangla (Bengali) or English.
            
            Generate {num_questions} questions with the following specifications:
            - Difficulty level: {difficulty}
            - Question types: {question_types}
            - Mix different question types if multiple types are requested
            - For multiple choice questions, provide 4 options labeled A, B, C, D
            - Always include the correct answer
            - Ensure questions are clear, educational, and test understanding of the content
            
            Return the response as a valid JSON array of question objects with this structure:
            [
                {{
                    "question": "Question text here?",
                    "question_type": "multiple_choice|short_answer|true_false",
                    "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"] (only for multiple_choice),
                    "correct_answer": "Correct answer here",
                    "difficulty": "{difficulty}",
                    "subject": "{subject}"
                }}
            ]
            """),
            ("user", "Content to generate questions from:\n\n{content}")
        ])
        
        # Format the prompt
        messages = prompt_template.format_messages(
            subject=subject,
            num_questions=num_questions,
            difficulty=difficulty,
            question_types=", ".join(question_types),
            content=content[:8000]  # Limit content length to avoid token limits
        )
        
        # Generate questions
        response = llm.invoke(messages)
        
        # Extract JSON from response
        response_text = response.content.strip()
        
        # Log response for debugging
        print(f"LLM Response: {response_text[:500]}...")  # Print first 500 chars
        
        if not response_text:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="LLM returned an empty response"
            )
        
        # Try to find JSON array in the response
        start_idx = response_text.find('[')
        end_idx = response_text.rfind(']') + 1
        
        if start_idx != -1 and end_idx != 0:
            json_str = response_text[start_idx:end_idx]
            questions_data = json.loads(json_str)
        else:
            # If no JSON array found, raise error with response preview
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not find JSON array in response. Response preview: {response_text[:200]}"
            )
        
        # Convert to Question objects
        questions = [Question(**q) for q in questions_data]
        
        # Create preview of extracted text
        text_preview = content[:500] + "..." if len(content) > 500 else content
        
        return QuestionGenerationResponse(
            success=True,
            subject=subject,
            total_questions=len(questions),
            questions=questions,
            extracted_text_preview=text_preview
        )
        
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse generated questions: {str(e)}. Response was: {response_text[:300] if 'response_text' in locals() else 'No response'}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating questions: {str(e)}"
        )


async def process_images_and_generate_questions(
    images: List[UploadFile],
    subject: str,
    num_questions: int = 10,
    difficulty: str = "medium",
    question_types: List[str] = None
) -> QuestionGenerationResponse:
    """
    Main controller to process images and generate questions
    """
    # Validate number of images
    if len(images) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one image is required"
        )
    
    # Validate image types
    valid_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    for image in images:
        if image.content_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type: {image.content_type}. Allowed types: jpeg, jpg, png, webp"
            )
    
    # Extract text from images
    extracted_content = await extract_text_from_images(images)
    
    if not extracted_content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No text could be extracted from the images"
        )
    
    # Generate questions from extracted content
    result = await generate_questions_from_content(
        content=extracted_content,
        subject=subject,
        num_questions=num_questions,
        difficulty=difficulty,
        question_types=question_types
    )
    
    return result
