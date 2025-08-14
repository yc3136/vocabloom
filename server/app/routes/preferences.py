from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models import User
from app.schemas import UserPreferences
from typing import Optional

router = APIRouter()

@router.get("/preferences")
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user preferences"""
    try:
        # Get user preferences from database
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Return preferences from JSONB field, with defaults
        user_prefs = user.preferences or {}
        return {
            "preferred_languages": user_prefs.get("preferred_languages", []),
            "child_age": user_prefs.get("child_age"),
            "child_name": user_prefs.get("child_name"),
            "content_privacy_default": user_prefs.get("content_privacy_default", "private")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get preferences: {str(e)}")

@router.post("/preferences")
async def save_preferences(
    preferences: UserPreferences,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save user preferences"""
    try:
        # Update user preferences in database
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update individual preference columns
        user.child_name = preferences.child_name
        user.child_age = preferences.child_age
        user.preferred_languages = preferences.preferred_languages or []
        user.content_privacy_default = preferences.content_privacy_default or "private"
        
        db.commit()
        db.refresh(user)
        
        # Return the updated preferences
        return {
            "preferred_languages": user.preferred_languages or [],
            "child_age": user.child_age,
            "child_name": user.child_name,
            "content_privacy_default": user.content_privacy_default or "private"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save preferences: {str(e)}") 