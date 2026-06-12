from fastapi import APIRouter, HTTPException
from typing import Any, Dict
from app.services.llm_service import generate_interview_questions, check_ollama_connection
from app.schemas.schemas import InterviewQuestionsResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
async def get_interview_health():
    """Health check for Interview module."""
    conn = await check_ollama_connection()
    return {
        "status": "ready",
        "llm_connected": conn.get("status") == "connected"
    }

@router.post("/test", response_model=InterviewQuestionsResponse)
async def test_interview_generation():
    """Test the Interview Question generation module with hardcoded sample data."""
    resume_data = {
        "skills": ["Python", "FastAPI", "SQL", "Docker"],
        "projects": ["AI Resume Analyzer", "Blockchain Game"]
    }
    
    jd_data = {
        "required_skills": ["Python", "FastAPI", "Docker", "AWS"]
    }

    try:
        result = await generate_interview_questions(
            resume_text=str(resume_data),
            job_description=str(jd_data)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Add Validation
    required_categories = ["technical_questions", "project_questions", "hr_questions"]
    required_difficulties = ["easy", "medium", "hard"]
    
    for category in required_categories:
        if category not in result:
            raise HTTPException(status_code=500, detail=f"Validation failed: Category {category} missing.")
            
        for diff in required_difficulties:
            if diff not in result[category]:
                raise HTTPException(status_code=500, detail=f"Validation failed: Difficulty {diff} missing in {category}.")
            
            questions = result[category][diff]
            if not isinstance(questions, list):
                raise HTTPException(status_code=500, detail=f"Validation failed: {diff} questions in {category} is not a list.")
            
            if len(questions) < 3:
                raise HTTPException(status_code=500, detail=f"Validation failed: Expected at least 3 {diff} questions in {category}, got {len(questions)}.")
            
            for q in questions:
                if not q or not str(q).strip():
                    raise HTTPException(status_code=500, detail=f"Validation failed: Found empty question in {category}.{diff}.")

    return result
