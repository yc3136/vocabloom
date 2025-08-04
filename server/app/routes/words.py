from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from ..database import get_db
from ..auth import get_current_user
from ..models import User, Translation, Flashcard
from ..schemas import WordSummary

router = APIRouter(prefix="/words", tags=["words"])


@router.get("/my", response_model=List[WordSummary])
async def get_user_words(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all unique words that the current user has translated,
    with their translations.
    """
    print(f"Getting words for user: {current_user.id}")
    
    # Get words from translation history (this is the source of truth for word lookups)
    translation_words = db.query(
        Translation.original_term,
        Translation.target_language,
        Translation.translation,
        Translation.explanation,
        func.min(Translation.created_at).label('created_at')
    ).filter(
        Translation.user_id == current_user.id
    ).group_by(
        Translation.original_term,
        Translation.target_language,
        Translation.translation,
        Translation.explanation
    ).order_by(
        func.min(Translation.created_at).desc()
    ).all()
    
    print(f"Found {len(translation_words)} translation words")
    
    # Convert to WordSummary objects
    word_summaries = []
    for word_data in translation_words:
        word_summary = WordSummary(
            original_word=word_data.original_term,
            target_language=word_data.target_language,
            translation=word_data.translation,
            explanation=word_data.explanation,
            examples=[],  # We'll add examples later when we store them
            created_at=word_data.created_at
        )
        word_summaries.append(word_summary)
    
    return word_summaries


@router.delete("/my/{original_word}")
async def delete_word_from_history(
    original_word: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a word from the user's translation history.
    This only affects the translation history, not flashcards.
    """
    # Delete all translations for this word by this user
    deleted_count = db.query(Translation).filter(
        Translation.user_id == current_user.id,
        Translation.original_term == original_word
    ).delete()
    
    db.commit()
    
    return {"message": f"Removed {deleted_count} translation(s) for '{original_word}' from history"} 