# pyrefly: ignore [missing-import]
from app.services import llm_service
# pyrefly: ignore [missing-import]
from fastapi import APIRouter
import time
from app.services.llm_service import check_ollama_connection, check_model_availability, generate_response
from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def get_health():
    """Check Ollama health and model availability."""
    conn_status = await check_ollama_connection()
    if conn_status.get("status") != "connected":
        return {
            "status": "unhealthy",
            "ollama_connected": False,
            "message": conn_status.get("message")
        }
        
    model_status = await check_model_availability()
    
    if model_status.get("status") != "available":
        return {
            "status": "unhealthy",
            "ollama_connected": True,
            "model": settings.OLLAMA_MODEL,
            "model_status": "unavailable",
            "error": model_status.get("message"),
            "available_models": model_status.get("available_models", [])
        }
        
    return {
        "status": "healthy",
        "ollama_connected": True,
        "model": settings.OLLAMA_MODEL,
        "model_status": "available"
    }

@router.get("/debug-test")
async def debug_test_llm():
    """Debug endpoint to test basic LLM connectivity using the same configuration as AI Analysis."""
    try:
        raw_response = await generate_response(prompt="Hello")
        return {
            "status": "success",
            "raw_response": raw_response
        }
    except Exception as e:
        return {
            "status": "error",
            "detail": str(e)
        }
