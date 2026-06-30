# pyrefly: ignore [missing-import]
from fastapi import FastAPI, Request, HTTPException
# pyrefly: ignore [missing-import]
from fastapi.responses import FileResponse
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

# Path to the React build directory
FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/dist"))

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

@app.get("/{full_path:path}")
async def serve_react_app(full_path: str, request: Request):
    """
    Catch-all route to serve the React SPA.
    - If the request targets an API endpoint, let it fail with 404 (or handle it if valid).
    - Otherwise, try to serve a static file from frontend/dist.
    - If the file doesn't exist, fallback to index.html for React Router.
    """
    # Exclude API routes from falling back to index.html
    api_prefix = settings.API_V1_STR.strip("/")
    if full_path.startswith(f"{api_prefix}/"):
        raise HTTPException(status_code=404, detail="Not Found")

    # Construct the path to the requested file
    file_path = os.path.join(FRONTEND_DIST, full_path)

    # If it's a specific file that exists in the dist folder, serve it
    if os.path.isfile(file_path):
        return FileResponse(file_path)

    # For unknown routes (e.g., /dashboard), serve index.html for React Router to handle
    index_path = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)

    # If index.html is missing, the frontend hasn't been built properly
    raise HTTPException(status_code=404, detail="Frontend build not found")
