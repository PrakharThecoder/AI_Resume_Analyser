from fastapi import APIRouter
from app.api.v1 import auth, resumes, jobs, analysis, ats, llm, ai_analysis, test_prompt, interview, dashboard, system, cache, docker

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
api_router.include_router(jobs.router, prefix="/job-description", tags=["job-description"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(ats.router, prefix="/ats", tags=["ats"])
api_router.include_router(llm.router, prefix="/llm", tags=["llm"])
api_router.include_router(ai_analysis.router, prefix="/ai-analysis", tags=["ai-analysis"])
api_router.include_router(test_prompt.router, tags=["test-prompt"])
api_router.include_router(interview.router, prefix="/interview", tags=["interview"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
api_router.include_router(cache.router, prefix="/cache", tags=["cache"])
api_router.include_router(docker.router, prefix="/docker", tags=["docker"])
