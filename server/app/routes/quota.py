from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict
from ..models import User
from ..auth import get_current_user
from ..redis_quota import (
    get_remaining_quota, 
    get_user_quotas, 
    reset_user_quota, 
    get_redis_health,
    clear_pending_generation,
    has_pending_generation
)

router = APIRouter(prefix="/quota", tags=["quota"])


@router.get("/")
async def get_user_quotas_endpoint(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Dict]:
    """Get quota information for all content types for the current user"""
    return get_user_quotas(current_user.id)


@router.get("/{content_type}")
async def get_content_type_quota(
    content_type: str,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """Get quota information for a specific content type"""
    quota_info = get_remaining_quota(current_user.id, content_type)
    
    if quota_info["limit"] == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No quota limit configured for {content_type}"
        )
    
    return quota_info


@router.post("/{content_type}/reset")
async def reset_quota(
    content_type: str,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """Reset quota for a specific content type (for testing)"""
    success = reset_user_quota(current_user.id, content_type)
    
    if success:
        return {"message": f"Quota reset successfully for {content_type}"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset quota"
        )


@router.get("/health/redis")
async def get_redis_health_endpoint() -> Dict:
    """Check Redis connection health"""
    return get_redis_health()


@router.post("/{content_type}/clear-pending")
async def clear_pending_generation_endpoint(
    content_type: str,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """Clear pending generation for the current user and content type"""
    # Check if there's actually a pending generation
    if not has_pending_generation(current_user.id, content_type):
        return {
            "message": f"No pending {content_type} generation found for user",
            "cleared": False
        }
    
    success = clear_pending_generation(current_user.id, content_type)
    
    if success:
        return {
            "message": f"Pending {content_type} generation cleared successfully",
            "cleared": True
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear pending generation"
        )


@router.get("/{content_type}/pending-status")
async def get_pending_status_endpoint(
    content_type: str,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """Check if user has any pending generations for a content type"""
    has_pending = has_pending_generation(current_user.id, content_type)
    
    return {
        "content_type": content_type,
        "has_pending": has_pending,
        "user_id": current_user.id
    } 