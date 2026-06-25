# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.staticfiles import StaticFiles
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import engine, Base

from app.api.api_v1.api import api_router
from app.core.exceptions import NotFoundException, not_found_exception_handler
from contextlib import asynccontextmanager
from app.services.llm_service import check_ollama_connection, check_model_availability
from app.core.logger import llm_logger
import httpx
import app.core.http_client as hc

import os

# Create database tables
Base.metadata.create_all(bind=engine)

# Ensure upload directory exists
os.makedirs("uploads/resumes", exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    hc.http_client = httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT)
    llm_logger.info("Performing startup Ollama connection check...")
    conn = await check_ollama_connection()
    if conn.get("status") == "connected":
        await check_model_availability()
    yield
    # Shutdown tasks
    if hc.http_client:
        await hc.http_client.aclose()

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0", openapi_url=f"{settings.API_V1_STR}/openapi.json", lifespan=lifespan)

app.add_exception_handler(NotFoundException, not_found_exception_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:80",
        "http://127.0.0.1:80"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Resume Analyzer API"}
