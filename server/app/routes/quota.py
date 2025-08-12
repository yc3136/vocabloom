from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict
from ..models import User
from ..auth import get_current_user
from ..redis_quota import get_remaining_quota, get_user_quotas, reset_user_quota

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