# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import engine, Base

from app.api.v1 import auth, resumes, jobs, analysis, ats, llm, ai_analysis, test_prompt, interview, dashboard
from app.core.exceptions import NotFoundException, not_found_exception_handler
from contextlib import asynccontextmanager
from app.services.llm_service import check_ollama_connection, check_model_availability
from app.core.logger import llm_logger

import os

# Create database tables
Base.metadata.create_all(bind=engine)

# Ensure upload directory exists
os.makedirs("uploads/resumes", exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    llm_logger.info("Performing startup Ollama connection check...")
    conn = await check_ollama_connection()
    if conn.get("status") == "connected":
        await check_model_availability()
    yield
    # Shutdown tasks

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0", openapi_url=f"{settings.API_V1_STR}/openapi.json", lifespan=lifespan)

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
app.include_router(llm.router, prefix=f"{settings.API_V1_STR}/llm", tags=["llm"])
app.include_router(ai_analysis.router, prefix=f"{settings.API_V1_STR}/ai-analysis", tags=["ai-analysis"])
app.include_router(test_prompt.router, prefix=f"{settings.API_V1_STR}", tags=["test-prompt"])
app.include_router(interview.router, prefix=f"{settings.API_V1_STR}/interview", tags=["interview"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["dashboard"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Resume Analyzer API"}
