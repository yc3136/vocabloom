from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import User
from ..schemas import Translation, TranslationCreate
from ..auth import get_current_user
from ..crud import get_translations, create_translation, update_translation_bookmark

router = APIRouter(prefix="/translations", tags=["translations"])


@router.get("/history", response_model=List[Translation])
async def get_translation_history(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get translation history for the current user"""
    translations = get_translations(db, current_user.id, skip=skip, limit=limit)
    return translations


@router.post("/save", response_model=Translation)
async def save_translation(
    translation: TranslationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a translation to user's history"""
    return create_translation(db, translation, current_user.id)


@router.put("/{translation_id}/bookmark")
async def toggle_translation_bookmark(
    translation_id: int,
    bookmarked: bool,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle bookmark status for a translation"""
    translation = update_translation_bookmark(db, translation_id, current_user.id, bookmarked)
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found"
        )
    return {"message": f"Translation {'bookmarked' if bookmarked else 'unbookmarked'} successfully"} 