from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Resume Schemas
class ResumeBase(BaseModel):
    filename: str

class ResumeCreate(ResumeBase):
    content: str
    owner_id: int

class ResumeResponse(ResumeBase):
    id: int
    upload_date: datetime
    owner_id: int
    analysis_status: str
    ats_score: Optional[float] = None

    class Config:
        from_attributes = True

# Job Description Schemas
class JobDescriptionAnalyzeRequest(BaseModel):
    job_description: str

class JobDescriptionAnalyzeResponse(BaseModel):
    job_id: int
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    experience_requirement: str = ""
    education_requirement: str = ""
    status: str = "success"

    class Config:
        from_attributes = True

# Analysis Schemas
class AnalysisBase(BaseModel):
    match_score: float
    ats_feedback: str
    llm_report: str

class AnalysisCreate(AnalysisBase):
    resume_id: int
    job_id: int

class AnalysisResponse(AnalysisBase):
    id: int
    resume_id: int
    job_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# AI Resume Analysis Schemas
class AIAnalysisRequest(BaseModel):
    resume_id: int
    job_id: int
    ats_score: float

class AIAnalysisResponse(BaseModel):
    objective_feedback: str
    missing_skills: List[str] = []
    improvement_recommendations: List[str] = []
    interview_preparation_advice: List[str] = []

# Parsed Resume Data Schemas
class ParsedResumeDataResponse(BaseModel):
    id: int
    resume_id: int
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: Optional[List[str]] = []
    education: Optional[List[str]] = []
    experience: Optional[List[str]] = []
    projects: Optional[List[str]] = []

    class Config:
        from_attributes = True

# ATS Schemas
class ATSCalculateRequest(BaseModel):
    resume_id: int
    job_description_id: int

class ATSCalculateResponse(BaseModel):
    ats_score: float
    skill_match_score: float
    experience_score: float
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    recommendations: List[str] = []

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "ats_score": 85.0,
                "skill_match_score": 25.0,
                "experience_score": 20.0,
                "matched_skills": ["Python", "FastAPI"],
                "missing_skills": ["Docker", "AWS"],
                "recommendations": ["Consider adding missing keywords like: Docker, AWS"]
            }
        }

# Interview Questions Schemas
class QuestionCategory(BaseModel):
    easy: List[str] = []
    medium: List[str] = []
    hard: List[str] = []

class InterviewQuestionsRequest(BaseModel):
    resume_text: str
    job_description: str

class InterviewQuestionsResponse(BaseModel):
    technical_questions: QuestionCategory
    project_questions: QuestionCategory
    hr_questions: QuestionCategory

# Dashboard Schemas
class ResumeSectionItem(BaseModel):
    name: str
    score: int

class DashboardSchema(BaseModel):
    base_ats_score: int
    ats_score: Optional[int] = None
    skill_match_percentage: int
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    strengths: List[str] = []
    weaknesses: List[str] = []
    recommendations: List[str] = []
    candidate_summary: str
    interview_tips: List[str] = []
    section_scores: dict
