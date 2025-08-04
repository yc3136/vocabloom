import hashlib
import json
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from .models import CachedTranslation
from .database import get_db


def hash_prompt(word: str, language: str, user_preferences: Optional[Dict[str, Any]] = None) -> str:
    """
    Create a deterministic hash of the prompt for caching.
    
    Args:
        word: The word to translate
        language: Target language
        user_preferences: User preferences that affect the prompt (child_name, child_age, etc.)
    
    Returns:
        SHA256 hash of the prompt data
    """
    # Create a deterministic prompt data structure
    prompt_data = {
        "word": word.lower().strip(),  # Normalize word
        "language": language,
        "child_name": user_preferences.get("child_name") if user_preferences else None,
        "child_age": user_preferences.get("child_age") if user_preferences else None,
        "learning_level": user_preferences.get("learning_level") if user_preferences else None,
    }
    
    # Create a deterministic string representation
    prompt_string = json.dumps(prompt_data, sort_keys=True)
    
    # Hash it
    return hashlib.sha256(prompt_string.encode()).hexdigest()


def get_cached_translation(db: Session, prompt_hash: str) -> Optional[CachedTranslation]:
    """
    Get a cached translation by prompt hash.
    
    Args:
        db: Database session
        prompt_hash: Hash of the prompt
    
    Returns:
        CachedTranslation if found, None otherwise
    """
    return db.query(CachedTranslation).filter(
        CachedTranslation.prompt_hash == prompt_hash
    ).first()


def cache_translation(
    db: Session, 
    prompt_hash: str, 
    word: str, 
    language: str, 
    response_data: Dict[str, Any]
) -> CachedTranslation:
    """
    Cache a translation response.
    
    Args:
        db: Database session
        prompt_hash: Hash of the prompt
        word: Original word
        language: Target language
        response_data: Full LLM response data (dict)
    
    Returns:
        Created CachedTranslation object
    """
    cached_translation = CachedTranslation(
        prompt_hash=prompt_hash,
        original_word=word,
        target_language=language,
        response_json=response_data
    )
    
    db.add(cached_translation)
    db.commit()
    db.refresh(cached_translation)
    
    return cached_translation





def get_cache_stats(db: Session) -> Dict[str, Any]:
    """
    Get cache statistics.
    
    Args:
        db: Database session
    
    Returns:
        Dictionary with cache statistics
    """
    total_cached = db.query(CachedTranslation).count()
    
    # Get recent translations
    recent_translations = db.query(CachedTranslation).order_by(
        CachedTranslation.id.desc()
    ).limit(10).all()
    
    return {
        "total_cached_translations": total_cached,
        "recent_translations": [
            {
                "word": ct.original_word,
                "language": ct.target_language
            }
            for ct in recent_translations
        ]
    } 