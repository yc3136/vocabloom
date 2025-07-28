from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import User
from ..schemas import Flashcard, FlashcardCreate, FlashcardUpdate, FlashcardPreview
from ..auth import get_current_user
from ..crud import (
    get_flashcards, get_flashcard, create_flashcard, 
    update_flashcard, delete_flashcard
)

router = APIRouter(prefix="/flashcards", tags=["flashcards"])


@router.get("/", response_model=List[Flashcard])
async def get_user_flashcards(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all flashcards for the current user"""
    flashcards = get_flashcards(db, current_user.id, skip=skip, limit=limit)
    return flashcards


@router.post("/", response_model=Flashcard)
async def create_user_flashcard(
    flashcard: FlashcardCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new flashcard for the current user"""
    return create_flashcard(db, flashcard, current_user.id)


@router.get("/{flashcard_id}", response_model=Flashcard)
async def get_user_flashcard(
    flashcard_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific flashcard by ID"""
    flashcard = get_flashcard(db, flashcard_id, current_user.id)
    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )
    return flashcard


@router.put("/{flashcard_id}", response_model=Flashcard)
async def update_user_flashcard(
    flashcard_id: int,
    flashcard_update: FlashcardUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a specific flashcard"""
    flashcard = update_flashcard(db, flashcard_id, flashcard_update, current_user.id)
    if not flashcard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )
    return flashcard


@router.delete("/{flashcard_id}")
async def delete_user_flashcard(
    flashcard_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific flashcard"""
    success = delete_flashcard(db, flashcard_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard not found"
        )
    return {"message": "Flashcard deleted successfully"}


@router.post("/preview", response_model=FlashcardPreview)
async def preview_flashcard(
    flashcard: FlashcardPreview
):
    """Preview a flashcard without saving it (no authentication required)"""
    return flashcard 