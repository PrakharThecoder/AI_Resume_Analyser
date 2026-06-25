# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, Resume, JobDescription, Analysis, ResumeAnalysis
from app.api.deps import get_current_user
from app.schemas.schemas import AnalysisResponse, AnalysisCreate, AIAnalysisRequest, AIAnalysisResponse, DashboardSchema
from app.services.ats_scorer import ATSScorerService
from app.services import llm_service
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

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

    parsed_resume_dict = {
        "skills": parsed_resume_data.skills,
        "education": parsed_resume_data.education,
        "experience": parsed_resume_data.experience,
        "projects": parsed_resume_data.projects,
        "email": parsed_resume_data.email,
        "phone": parsed_resume_data.phone
    }
    
    parsed_jd_dict = {
        "required_skills": job.required_skills,
        "preferred_skills": job.preferred_skills,
        "experience_requirement": job.experience_requirement,
        "education_requirement": job.education_requirement
    }
    
    # Call Deterministic ATS Scorer
    scorer = ATSScorerService()
    base_result = scorer.calculate_base_score(resume.content, parsed_resume_dict)
    jd_result = scorer.calculate_job_match_score(resume.content, parsed_resume_dict, parsed_jd_dict)
    
    deterministic_stats = {
        "base_ats_score": base_result["base_ats_score"],
        "ats_score": jd_result["ats_score"],
        "skill_match_percentage": jd_result["skill_match_percentage"],
        "matched_skills": jd_result["matched_skills"],
        "missing_skills": jd_result["missing_skills"],
        "section_scores": base_result["section_scores"]
    }
    
    # Call LLM Service
    llm_insights = await llm_service.generate_ai_resume_analysis(resume.content, deterministic_stats)
    
    new_analysis = Analysis(
        resume_id=request.resume_id,
        job_id=request.job_id,
        match_score=jd_result["ats_score"],
        ats_feedback=json.dumps(deterministic_stats),
        llm_report="" # Not used anymore
    )
    db.add(new_analysis)
    
    resume_analysis = ResumeAnalysis(
        user_id=current_user.id,
        base_ats_score=deterministic_stats["base_ats_score"],
        ats_score=deterministic_stats["ats_score"],
        role=None,
        skill_match_percentage=deterministic_stats["skill_match_percentage"],
        matched_skills=deterministic_stats["matched_skills"],
        missing_skills=deterministic_stats["missing_skills"],
        resume_sections=deterministic_stats["section_scores"],
        candidate_summary=llm_insights.get("candidate_summary", ""),
        strengths=llm_insights.get("strengths", []),
        weaknesses=llm_insights.get("weaknesses", []),
        recommendations=llm_insights.get("recommendations", []),
        interview_tips=llm_insights.get("interview_tips", [])
    )
    db.add(resume_analysis)
    
    # Update Resume score
    resume.ats_score = jd_result["ats_score"]
    
    db.commit()
    db.refresh(new_analysis)
    db.refresh(resume_analysis)
    
    logger.info(f"Saved analysis {resume_analysis.id} for user {current_user.id}")
    return new_analysis

@router.get("/latest", response_model=DashboardSchema)
async def get_latest_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    latest = (
        db.query(ResumeAnalysis)
        .filter(ResumeAnalysis.user_id == current_user.id)
        .order_by(ResumeAnalysis.created_at.desc())
        .first()
    )

    if not latest:
        raise HTTPException(
            status_code=404,
            detail="No analysis found for this user"
        )

    response_data = {
        "base_ats_score": latest.base_ats_score or 0,
        "ats_score": latest.ats_score,
        "skill_match_percentage": latest.skill_match_percentage or 0,
        "matched_skills": latest.matched_skills or [],
        "missing_skills": latest.missing_skills or [],
        "section_scores": latest.resume_sections or {},
        "candidate_summary": latest.candidate_summary or "No analysis generated yet.",
        "strengths": latest.strengths or [],
        "weaknesses": latest.weaknesses or [],
        "recommendations": latest.recommendations or [],
        "interview_tips": latest.interview_tips or []
    }

    logger.info(f"Returning dashboard analytics for user {current_user.id}")
    return response_data

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

@router.post("/ai-insights", response_model=AIAnalysisResponse)
async def get_ai_resume_insights(
    request: AIAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resume = db.query(Resume).filter(Resume.id == request.resume_id, Resume.owner_id == current_user.id).first()
    job = db.query(JobDescription).filter(JobDescription.id == request.job_id, JobDescription.owner_id == current_user.id).first()
    
    if not resume or not job:
        raise HTTPException(status_code=404, detail="Resume or Job not found")
        
    parsed_resume_data = resume.parsed_data
    if not parsed_resume_data:
        raise HTTPException(status_code=400, detail="Resume has not been fully parsed yet.")

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

    result = await llm_service.generate_ai_resume_analysis(
        parsed_resume_dict, 
        parsed_jd_dict, 
        request.ats_score
    )
    
    return result
