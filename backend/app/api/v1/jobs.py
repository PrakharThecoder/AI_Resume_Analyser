# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db
from app.db.models import User, JobDescription
from app.api.deps import get_current_user_optional
from app.schemas.schemas import JobDescriptionAnalyzeRequest, JobDescriptionAnalyzeResponse
import traceback
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=503, detail="Database connection failed")

@router.post("/analyze", response_model=JobDescriptionAnalyzeResponse)
async def analyze_jd(
    request: JobDescriptionAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    logger.info("Received request to /analyze endpoint")
    if len(request.job_description) < 50:
        logger.warning("Job description rejected: less than 50 characters")
        raise HTTPException(status_code=400, detail="Job description must be at least 50 characters long.")
    if len(request.job_description) > 10000:
        logger.warning("Job description rejected: more than 10000 characters")
        raise HTTPException(status_code=400, detail="Job description must be at most 10000 characters long.")
    
    from app.services.jd_service import JDParserService
    
    try:
        parser_service = JDParserService()
        logger.info("Calling JDParserService to parse text")
        parsed_data = parser_service.parse_text(request.job_description)
        
        logger.info("Starting database insertion step...")
        new_job = JobDescription(
            job_title=parsed_data.get("job_title", "Unknown Title"),
            raw_job_description=request.job_description,
            required_skills=parsed_data.get("required_skills", []),
            preferred_skills=parsed_data.get("preferred_skills", []),
            experience_requirement=parsed_data.get("experience_requirement", ""),
            education_requirement=parsed_data.get("education_requirement", ""),
            owner_id=current_user.id if current_user else None
        )
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        logger.info(f"Database insertion step completed successfully. Job ID: {new_job.id}")
        
        return {
            "job_id": new_job.id,
            "required_skills": new_job.required_skills,
            "preferred_skills": new_job.preferred_skills,
            "experience_requirement": new_job.experience_requirement,
            "education_requirement": new_job.education_requirement,
            "status": "success"
        }
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Failed to parse JD: {str(e)}\n{error_traceback}")
        
        # Return structured error message with traceback during development
        raise HTTPException(
            status_code=500, 
            detail={
                "message": "Error occurred while parsing the JD",
                "error": str(e),
                "traceback": error_traceback
            }
        )
