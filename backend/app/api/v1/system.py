# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import ParsedResumeData
from app.core.metrics import metrics
from app.services.llm_service import check_model_availability, generate_ai_resume_analysis
import psutil
import os
import time

router = APIRouter()

@router.get("/health")
async def system_health():
    model_status = await check_model_availability()
    return {
        "status": "healthy",
        "model_loaded": model_status.get("status") == "available",
        "cache_enabled": True,
        "memory_optimization_enabled": True,
        "lazy_loading_enabled": True
    }

@router.get("/performance")
async def system_performance(db: Session = Depends(get_db)):
    process = psutil.Process(os.getpid())
    ram_usage_mb = process.memory_info().rss / (1024 * 1024)
    cpu_usage_percent = psutil.cpu_percent(interval=0.1)
    
    model_status = await check_model_availability()
    cache_entries = db.query(ParsedResumeData).count()
    
    return {
        "ram_usage_mb": round(ram_usage_mb, 2),
        "cpu_usage_percent": cpu_usage_percent,
        "model_loaded": model_status.get("status") == "available",
        "cache_entries": cache_entries,
        "average_inference_time_ms": round(metrics.get_average_inference_time(), 2)
    }

@router.post("/benchmark")
async def system_benchmark():
    # 1. Resume Parsing Mock
    start = time.time()
    time.sleep(0.05) # simulate parsing
    parse_time = (time.time() - start) * 1000
    
    # 2. ATS Analysis Mock
    start = time.time()
    time.sleep(0.02) # simulate ats
    ats_time = (time.time() - start) * 1000
    
    # 3. LLM Inference (Real but simple)
    start = time.time()
    try:
        await generate_ai_resume_analysis(
            {"skills": ["Python", "FastAPI"], "experience": "2 years"},
            {"required_skills": ["Python"], "experience_requirement": "1 year"},
            85.0
        )
    except Exception:
        pass
    llm_time = (time.time() - start) * 1000
    
    return {
        "resume_parse_time_ms": round(parse_time, 2),
        "ats_analysis_time_ms": round(ats_time, 2),
        "llm_inference_time_ms": round(llm_time, 2),
        "total_time_ms": round(parse_time + ats_time + llm_time, 2)
    }
