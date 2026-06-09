from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, Resume, JobDescription, ATSResult
from app.api.deps import get_current_user_optional
from app.schemas.schemas import ATSCalculateRequest, ATSCalculateResponse
from app.services.ats_service import ATSScorerService

router = APIRouter()

@router.post("/calculate", response_model=ATSCalculateResponse)
async def calculate_ats_score(
    request: ATSCalculateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Calculate an ATS score deterministically using rule-based logic.
    """
    # Fetch Resume
    resume = db.query(Resume).filter(Resume.id == request.resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Fetch Job Description
    job = db.query(JobDescription).filter(JobDescription.id == request.job_description_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")

    # Ensure parsing is complete
    parsed_resume_data = resume.parsed_data
    if not parsed_resume_data:
        raise HTTPException(status_code=400, detail="Resume has not been fully parsed yet.")

    # Construct dicts for ATS Scorer
    parsed_resume_dict = {
        "skills": parsed_resume_data.skills,
        "education": parsed_resume_data.education,
        "experience": parsed_resume_data.experience,
        "projects": parsed_resume_data.projects
    }
    
    parsed_jd_dict = {
        "required_skills": job.required_skills,
        "preferred_skills": job.preferred_skills,
        "experience_requirement": job.experience_requirement,
        "education_requirement": job.education_requirement
    }
    
    # Calculate score
    scorer = ATSScorerService()
    result = scorer.score(resume.content, parsed_resume_dict, parsed_jd_dict)
    
    # Save Result
    new_ats_result = ATSResult(
        resume_id=request.resume_id,
        job_description_id=request.job_description_id,
        ats_score=result["ats_score"]
    )
    db.add(new_ats_result)
    db.commit()
    db.refresh(new_ats_result)
    
    return result
