# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.services.llm_service import generate_ai_resume_analysis, check_ollama_connection
from pydantic import BaseModel, ValidationError, Field

router = APIRouter()

# Simple schema for test response validation
class TestValidationSchema(BaseModel):
    objective_feedback: str = Field(..., min_length=1)
    missing_skills: list[str]
    improvement_recommendations: list[str]
    interview_preparation_advice: list[str]

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
    # Hardcoded sample data
    resume_data = {
        "skills": ["Python", "FastAPI", "SQL"],
        "experience": "1 year",
        "education": "B.Tech"
    }
    
    jd_data = {
        "required_skills": ["Python", "FastAPI", "Docker", "AWS"],
        "experience_requirement": "2 years"
    }
    
    ats_score = {
        "ats_score": 65,
        "matched_skills": ["Python", "FastAPI"],
        "missing_skills": ["Docker", "AWS"]
    }

    # Execute LLM analysis
    try:
        result = await generate_ai_resume_analysis(
            parsed_resume=resume_data,
            parsed_jd=jd_data,
            ats_score=ats_score["ats_score"]
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
