# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.services.llm_service import generate_ai_resume_analysis, check_ollama_connection
from pydantic import BaseModel, ValidationError, Field

router = APIRouter()

# Simple schema for test response validation
class TestValidationSchema(BaseModel):
    candidate_summary: str = Field(..., min_length=1)
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]
    interview_tips: list[str]

@router.get("/health")
async def get_health():
    """Health check for AI Analysis module."""
    conn = await check_ollama_connection()
    return {
        "llm_connected": conn.get("status") == "connected",
        "analysis_module": "ready"
    }

@router.post("/test")
async def test_ai_analysis():
    """Test the AI Analysis module with hardcoded sample data."""
    resume_text = "Experienced Software Engineer with 1 year of experience in Python, FastAPI, and SQL. Education: B.Tech."
    
    deterministic_stats = {
        "base_ats_score": 65,
        "ats_score": 65,
        "skill_match_percentage": 50.0,
        "matched_skills": ["Python", "FastAPI"],
        "missing_skills": ["Docker", "AWS"],
        "section_scores": {"skills": 10, "experience": 10, "education": 10}
    }

    # Execute LLM analysis
    try:
        result = await generate_ai_resume_analysis(
            resume_text=resume_text,
            deterministic_stats=deterministic_stats
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Add Validation
    try:
        # Verify candidate_summary is not empty, arrays exist, etc.
        # Pydantic will raise ValueError if constraints are not met
        TestValidationSchema(**result)
    except ValidationError as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Validation failed for LLM response: {e.errors()}"
        )
        
    return result
