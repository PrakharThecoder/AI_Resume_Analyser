# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException
from app.services.llm_service import generate_response
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/test-prompt")
async def test_prompt_engineering():
    """Test the Prompt Engineering Service execution."""
    
    sample_resume = "Software Engineer with Python and FastAPI experience. Built REST APIs and machine learning projects."
    sample_jd = "Looking for a Backend Developer skilled in Python, FastAPI, Docker, Kubernetes, and AWS."
    
    from app.core.prompts import SYSTEM_PROMPT
    user_prompt = f"Resume:\n{sample_resume}\n\nJob Description:\n{sample_jd}"
    try:
        response_text = await generate_response(
            prompt=user_prompt,
            system_prompt=SYSTEM_PROMPT
        )
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Ollama connection error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM execution failed: {e}")
        
    if not response_text:
        raise HTTPException(status_code=500, detail="Missing response from LLM.")

    # Validation
    required_sections = [
        "Objective Feedback",
        "Missing Skills",
        "Improvement Recommendations",
        "Interview Preparation Advice"
    ]
    
    missing_sections = []
    for section in required_sections:
        # Check case-insensitively or exactly, the prompt asks for exact.
        if section not in response_text and section.upper() not in response_text and section.lower() not in response_text.lower():
            missing_sections.append(section)
            
    if missing_sections:
        error_msg = f"Prompt execution failed. Missing required sections: {', '.join(missing_sections)}"
        logger.error(f"{error_msg}. Raw response: {response_text}")
        raise HTTPException(status_code=500, detail=error_msg)
        
    return {
        "status": "success",
        "analysis": response_text
    }
