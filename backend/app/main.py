# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import engine, Base

from app.api.v1 import auth, resumes, jobs, analysis, ats
from app.core.exceptions import NotFoundException, not_found_exception_handler


import os

# Create database tables
Base.metadata.create_all(bind=engine)

# Ensure upload directory exists
os.makedirs("uploads/resumes", exist_ok=True)

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0", openapi_url=f"{settings.API_V1_STR}/openapi.json")

app.add_exception_handler(NotFoundException, not_found_exception_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(resumes.router, prefix=f"{settings.API_V1_STR}/resumes", tags=["resumes"])
app.include_router(jobs.router, prefix=f"{settings.API_V1_STR}/job-description", tags=["job-description"])
app.include_router(analysis.router, prefix=f"{settings.API_V1_STR}/analysis", tags=["analysis"])
app.include_router(ats.router, prefix=f"{settings.API_V1_STR}/ats", tags=["ats"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Resume Analyzer API"}
