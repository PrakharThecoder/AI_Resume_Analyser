from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    resumes = relationship("Resume", back_populates="owner")
    jobs = relationship("JobDescription", back_populates="owner")

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_path = Column(String)
    file_size = Column(Integer)
    content = Column(Text) # Extracted text
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="resumes")
    analyses = relationship("Analysis", back_populates="resume")
    parsed_data = relationship("ParsedResumeData", back_populates="resume", uselist=False)

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String, index=True)
    raw_job_description = Column(Text)
    required_skills = Column(JSON)
    preferred_skills = Column(JSON)
    experience_requirement = Column(String)
    education_requirement = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="jobs")
    analyses = relationship("Analysis", back_populates="job")

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    job_id = Column(Integer, ForeignKey("job_descriptions.id"))
    match_score = Column(Float)
    ats_feedback = Column(Text) # JSON or Text
    llm_report = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    resume = relationship("Resume", back_populates="analyses")
    job = relationship("JobDescription", back_populates="analyses")

class ParsedResumeData(Base):
    __tablename__ = "parsed_resume_data"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), unique=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    skills = Column(JSON)
    education = Column(JSON)
    experience = Column(JSON)
    projects = Column(JSON)

    resume = relationship("Resume", back_populates="parsed_data")

class ATSResult(Base):
    __tablename__ = "ats_results"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id"))
    ats_score = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    resume = relationship("Resume")
    job = relationship("JobDescription")
