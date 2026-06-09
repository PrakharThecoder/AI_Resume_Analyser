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

router = APIRouter()

@router.get("/", response_model=list[ResumeResponse])
def get_resumes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Resume).filter(Resume.owner_id == current_user.id).all()

@router.post("/upload-resume")
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
    
    return {
        "resume_id": new_resume.id,
        "filename": new_resume.filename,
        "upload_status": "success"
    }

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
        parser_service = ResumeParserService()
        parsed_data = parser_service.parse(resume.file_path)
        
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
        
        existing_record = db.query(ParsedResumeData).filter(ParsedResumeData.resume_id == resume.id).first()
        if existing_record:
            for key, value in parsed_data.items():
                setattr(existing_record, key, value)
            db.commit()
            db.refresh(existing_record)
            return existing_record
        else:
            db.add(parsed_record)
            db.commit()
            db.refresh(parsed_record)
            return parsed_record
            
    except Exception as e:
        logger.error(f"Failed to parse resume: {str(e)}")
        raise HTTPException(status_code=500, detail="Error occurred while parsing the resume")
