# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import ParsedResumeData
from app.core.cache_manager import cache_manager

router = APIRouter()

@router.get("/stats")
def get_cache_stats(db: Session = Depends(get_db)):
    return {
        "cache_enabled": True,
        "cached_resumes": cache_manager.get_cached_resumes_count(),
        "cache_hits": cache_manager.cache_hits,
        "cache_misses": cache_manager.cache_misses
    }

@router.get("/debug")
def get_cache_debug(db: Session = Depends(get_db)):
    return {
        "cache_initialized": True,
        "cache_entries": cache_manager.get_cached_resumes_count(),
        "cache_keys": cache_manager.get_cache_keys(),
        "cache_hits": cache_manager.cache_hits,
        "cache_misses": cache_manager.cache_misses,
        "cache_backend": "file"
    }

@router.post("/test")
def test_cache():
    import uuid
    test_hash = f"test_{uuid.uuid4().hex}"
    test_data = {"status": "test", "value": 123}
    
    # Write to cache
    cache_manager.store_entry(test_hash, test_data)
    
    # Read from cache
    retrieved = cache_manager.get_entry(test_hash)
    
    return {
        "write_success": True,
        "read_success": retrieved is not None and retrieved.get("value") == 123,
        "cache_hit_detected": cache_manager.cache_hits > 0
    }
