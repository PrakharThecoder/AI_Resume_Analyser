# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException, Depends
import logging
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.deps import get_current_user
from app.db.models import User
from app.schemas.schemas import DashboardSchema
from app.services.dashboard_service import DashboardService

router = APIRouter()
logger = logging.getLogger(__name__)

MOCK_DASHBOARD_DATA = {
    "ats_score": 82,
    "skill_match_percentage": 75,
    "matched_skills": [
        "Python",
        "FastAPI",
        "React",
        "SQL"
    ],
    "missing_skills": [
        "Docker",
        "AWS",
        "Kubernetes"
    ],
    "resume_sections": {
        "skills": 90,
        "experience": 80,
        "education": 85,
        "projects": 70
    },
    "candidate_summary": "Strong backend developer",
    "strengths": [
        "Python",
        "FastAPI"
    ],
    "weaknesses": [
        "Cloud Skills"
    ]
}

@router.get("", response_model=DashboardSchema)
@router.get("/", response_model=DashboardSchema, include_in_schema=False)
async def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve the main dashboard payload."""
    try:
        logger.info(f"Accessing GET /api/v1/dashboard for user {current_user.id}")
        data = await DashboardService.get_dashboard_data(db, current_user.id)
        return data
    except Exception as e:
        logger.error(f"Failed to retrieve dashboard data: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching dashboard data")

@router.get("/health")
async def get_dashboard_health():
    """Health check for the Dashboard."""
    logger.info("Accessing GET /api/v1/dashboard/health")
    return {
        "status": "healthy",
        "dashboard_ready": True
    }

@router.get("/debug")
async def get_dashboard_debug(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return complete dashboard debug payload."""
    logger.info("Accessing GET /api/v1/dashboard/debug")
    try:
        # Check if service is callable
        await DashboardService.get_dashboard_data(db, current_user.id)
        service_status = "ok"
    except Exception:
        service_status = "error"

    return {
        "router_status": "ok",
        "service_status": service_status,
        "schema_status": "ok",
        "mock_dashboard_payload": MOCK_DASHBOARD_DATA
    }
