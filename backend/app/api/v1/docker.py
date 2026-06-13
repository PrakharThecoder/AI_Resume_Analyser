# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db
import httpx
import os

router = APIRouter()

@router.get("/status")
async def get_docker_status(db: Session = Depends(get_db)):
    status = {
        "frontend_connected": True,  # Assumed true if request reaches backend via frontend proxy, or true if running
        "backend_running": True,
        "ollama_connected": False,
        "model_loaded": False,
        "database_connected": False
    }

    # 1. Check Database
    try:
        db.execute(text("SELECT 1"))
        status["database_connected"] = True
    except Exception:
        pass

    # 2. Check Ollama Connection & Model
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    model_name = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
    
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{ollama_host}/api/tags")
            if response.status_code == 200:
                status["ollama_connected"] = True
                data = response.json()
                models = [m.get("name") for m in data.get("models", [])]
                if model_name in models or f"{model_name}:latest" in models:
                    status["model_loaded"] = True
    except Exception:
        pass

    return status
