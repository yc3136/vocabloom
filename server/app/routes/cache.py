from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..caching import get_cache_stats

router = APIRouter(prefix="/cache", tags=["cache"])


@router.get("/stats")
async def get_cache_statistics(db: Session = Depends(get_db)):
    """
    Get cache statistics for monitoring and analytics.
    This endpoint is public for transparency about caching performance.
    """
    return get_cache_stats(db) 