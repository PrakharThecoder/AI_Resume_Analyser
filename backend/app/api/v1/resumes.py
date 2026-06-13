# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, Resume
from app.api.deps import get_current_user, get_current_user_optional
from app.schemas.schemas import ResumeResponse, ParsedResumeDataResponse
from app.utils.pdf_parser import parse_pdf
import io
import os
import shutil
import hashlib

router = APIRouter()

@router.get("/", response_model=list[ResumeResponse])
def get_resumes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Resume).filter(Resume.owner_id == current_user.id).all()

@router.post("/upload", response_model=ResumeResponse)
async def upload_resume_new(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")
    
    user_id_prefix = current_user.id if current_user else "test"
    file_path = f"uploads/resumes/{user_id_prefix}_{file.filename}"
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    file.file.seek(0)
    content = await file.read()
    text = parse_pdf(content)
    
    new_resume = Resume(
        filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        content=text,
        owner_id=current_user.id if current_user else None
    )
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)
    
    return new_resume

@router.post("/parse-resume/{resume_id}", response_model=ParsedResumeDataResponse)
async def parse_resume_endpoint(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    if current_user and resume.owner_id and resume.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to parse this resume")
        
    from app.services.resume_parser import ResumeParserService
    from app.db.models import ParsedResumeData
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        from app.core.cache_manager import cache_manager
        file_hash = hashlib.sha256(resume.content.encode('utf-8')).hexdigest()
        
        # Check Persistent Cache first
        cached_data = cache_manager.get_entry(file_hash)
        if cached_data:
            parsed_data = cached_data
        else:
            parser_service = ResumeParserService()
            parsed_data = parser_service.parse(resume.file_path)
            # Store the result in the cache
            cache_manager.store_entry(file_hash, parsed_data)
            
        # Update Database Record
        existing_record = db.query(ParsedResumeData).filter(ParsedResumeData.resume_id == resume.id).first()
        if existing_record:
            for key, value in parsed_data.items():
                if hasattr(existing_record, key) and key != "id" and key != "resume_id":
                    setattr(existing_record, key, value)
            db.commit()
            db.refresh(existing_record)
            return existing_record
        
        parsed_record = ParsedResumeData(
            resume_id=resume.id,
            name=parsed_data.get("name"),
            email=parsed_data.get("email"),
            phone=parsed_data.get("phone"),
            skills=parsed_data.get("skills", []),
            education=parsed_data.get("education", []),
            experience=parsed_data.get("experience", []),
            projects=parsed_data.get("projects", [])
        )
        
        db.add(parsed_record)
        db.commit()
        db.refresh(parsed_record)
        return parsed_record
            
    except Exception as e:
        logger.error(f"Failed to parse resume: {str(e)}")
        raise HTTPException(status_code=500, detail="Error occurred while parsing the resume")

@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.owner_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    try:
        if os.path.exists(resume.file_path):
            os.remove(resume.file_path)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Could not delete file {resume.file_path}: {e}")
        
    db.delete(resume)
    db.commit()
    return {"status": "success", "detail": "Resume deleted"}

@router.post("/{resume_id}/analyze")
async def analyze_resume(
    resume_id: int,
    role: str = "Software Engineer",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.owner_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    try:
        from app.services.resume_parser import ResumeParserService
        parser_service = ResumeParserService()
        parsed_data = parser_service.parse(resume.file_path)
        
        parsed_resume_dict = {
            "skills": parsed_data.get("skills", []),
            "education": parsed_data.get("education", []),
            "experience": parsed_data.get("experience", []),
            "projects": parsed_data.get("projects", []),
            "email": parsed_data.get("email"),
            "phone": parsed_data.get("phone")
        }
        
        from app.services.ats_scorer import ATSScorerService
        scorer = ATSScorerService()
        
        base_result = scorer.calculate_base_score(resume.content, parsed_resume_dict)
        role_result = scorer.get_role_benchmark_skills(role, resume.content, parsed_resume_dict)
        
        deterministic_stats = {
            "base_ats_score": base_result["base_ats_score"],
            "ats_score": None, # No JD
            "skill_match_percentage": role_result["skill_match_percentage"],
            "matched_skills": role_result["matched_skills"],
            "missing_skills": role_result["missing_skills"],
            "section_scores": base_result["section_scores"]
        }
        
        from app.services import llm_service
        llm_insights = await llm_service.generate_ai_resume_analysis(resume.content, deterministic_stats)
        
        # Save to ResumeAnalysis
        from app.db.models import ResumeAnalysis
        
        resume_analysis = ResumeAnalysis(
            user_id=current_user.id,
            base_ats_score=deterministic_stats["base_ats_score"],
            ats_score=None,
            role=role,
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
        
        resume.ats_score = deterministic_stats["base_ats_score"]
        resume.analysis_status = "Completed"
        
        db.commit()
        db.refresh(resume)
        
        return {
            "status": "success",
            "ats_score": resume.ats_score,
            "analysis_status": resume.analysis_status
        }
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Analysis failed: {str(e)}")
        resume.analysis_status = "Failed"
        db.commit()
        raise HTTPException(status_code=500, detail="Error occurred during analysis")
