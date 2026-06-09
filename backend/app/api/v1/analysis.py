from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, Resume, JobDescription, Analysis
from app.api.deps import get_current_user
from app.schemas.schemas import AnalysisResponse, AnalysisCreate
from app.services.ats_scorer import ATSScorerService
import json

router = APIRouter()

@router.post("/", response_model=AnalysisResponse)
async def create_analysis(
    request: AnalysisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify ownership
    resume = db.query(Resume).filter(Resume.id == request.resume_id, Resume.owner_id == current_user.id).first()
    job = db.query(JobDescription).filter(JobDescription.id == request.job_id, JobDescription.owner_id == current_user.id).first()
    
    if not resume or not job:
        raise HTTPException(status_code=404, detail="Resume or Job not found")
        
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
    
    # Call Deterministic ATS Scorer
    scorer = ATSScorerService()
    result = scorer.score(resume.content, parsed_resume_dict, parsed_jd_dict)
    
    new_analysis = Analysis(
        resume_id=request.resume_id,
        job_id=request.job_id,
        match_score=result["ats_score"],
        ats_feedback=json.dumps({
            "matched_skills": result["matched_skills"],
            "missing_skills": result["missing_skills"],
            "recommendations": result["recommendations"],
            "breakdown": result["breakdown"]
        }),
        llm_report="" # Not used anymore
    )
    db.add(new_analysis)
    db.commit()
    db.refresh(new_analysis)
    return new_analysis

@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    analysis = db.query(Analysis).join(Resume).filter(
        Analysis.id == analysis_id, 
        Resume.owner_id == current_user.id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis
