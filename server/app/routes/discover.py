from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, func, or_, and_
from typing import List, Optional
from ..database import get_db
from ..models import Flashcard, Story, Image, Translation
from ..schemas import Flashcard as FlashcardSchema, Story as StorySchema, Image as ImageSchema, Translation as TranslationSchema
from datetime import datetime, timedelta

router = APIRouter(prefix="/discover", tags=["discover"])

# Age group mapping
AGE_GROUPS = {
    "toddler": (1, 3),
    "preschool": (4, 5),
    "elementary": (6, 10),
    "middle_school": (11, 13)
}

@router.get("/")
async def discover_content(
    search: Optional[str] = Query(None, description="Search term for original word, translation, or story content"),
    language: Optional[str] = Query(None, description="Filter by target language"),
    age_group: Optional[str] = Query(None, description="Filter by age group (toddler, preschool, elementary, middle_school)"),
    content_type: Optional[str] = Query(None, description="Filter by content type (flashcards, stories, images, translations)"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    db: Session = Depends(get_db)
):
    """
    Discover public content with search and filtering capabilities.
    Returns a unified feed of all content types in descending order by creation time.
    """
    try:
        content_items = []
        
        # Get flashcards
        if not content_type or content_type == "flashcards":
            flashcard_query = db.query(Flashcard)
            
            # Apply search filter
            if search:
                search_term = f"%{search}%"
                flashcard_query = flashcard_query.filter(
                    or_(
                        Flashcard.original_word.ilike(search_term),
                        Flashcard.translated_word.ilike(search_term)
                    )
                )
            
            # Apply language filter
            if language:
                flashcard_query = flashcard_query.filter(Flashcard.target_language == language)
            
            flashcards = flashcard_query.order_by(Flashcard.created_at.desc()).offset(skip).limit(limit).all()
            
            for flashcard in flashcards:
                content_items.append({
                    "id": flashcard.id,
                    "content_type": "flashcard",
                    "original_word": flashcard.original_word,
                    "translated_word": flashcard.translated_word,
                    "target_language": flashcard.target_language,
                    "example_sentences": flashcard.example_sentences,
                    "created_at": flashcard.created_at.isoformat() if flashcard.created_at else None,
                    "story_title": None,
                    "story_content": None,
                    "story_theme": None,
                    "target_age_range": None,
                    "image_url": None,
                    "translation": None,
                    "explanation": None,
                    "user": {
                        "email": flashcard.user.email if flashcard.user else None
                    }
                })
        
        # Get stories
        if not content_type or content_type == "stories":
            story_query = db.query(Story)
            
            # Apply search filter
            if search:
                search_term = f"%{search}%"
                story_query = story_query.filter(
                    or_(
                        Story.story_title.ilike(search_term),
                        Story.story_content.ilike(search_term)
                    )
                )
            
            # Apply language filter
            if language:
                story_query = story_query.filter(Story.target_language == language)
            
            # Apply age group filter
            if age_group and age_group in AGE_GROUPS:
                story_query = story_query.filter(Story.target_age_range == age_group)
            
            stories = story_query.order_by(Story.created_at.desc()).offset(skip).limit(limit).all()
            
            for story in stories:
                content_items.append({
                    "id": story.id,
                    "content_type": "story",
                    "original_word": None,
                    "translated_word": None,
                    "target_language": story.target_language,
                    "example_sentences": None,
                    "created_at": story.created_at.isoformat() if story.created_at else None,
                    "story_title": story.story_title,
                    "story_content": story.story_content,
                    "story_theme": story.story_theme,
                    "target_age_range": story.target_age_range,
                    "image_url": None,
                    "translation": None,
                    "explanation": None,
                    "user": {
                        "email": story.user.email if story.user else None
                    }
                })
        
        # Get images
        if not content_type or content_type == "images":
            image_query = db.query(Image).filter(Image.status == "completed")
            
            # Apply search filter
            if search:
                search_term = f"%{search}%"
                image_query = image_query.filter(
                    or_(
                        Image.original_word.ilike(search_term),
                        Image.translated_word.ilike(search_term)
                    )
                )
            
            # Apply language filter
            if language:
                image_query = image_query.filter(Image.target_language == language)
            
            images = image_query.order_by(Image.created_at.desc()).offset(skip).limit(limit).all()
            
            for image in images:
                content_items.append({
                    "id": image.id,
                    "content_type": "image",
                    "original_word": image.original_word,
                    "translated_word": image.translated_word,
                    "target_language": image.target_language,
                    "example_sentences": None,
                    "created_at": image.created_at.isoformat() if image.created_at else None,
                    "story_title": None,
                    "story_content": None,
                    "story_theme": None,
                    "target_age_range": None,
                    "image_url": image.image_url,
                    "translation": None,
                    "explanation": None,
                    "user": {
                        "email": image.user.email if image.user else None
                    }
                })
        
        # Sort all content by creation date (newest first)
        content_items.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Apply pagination to the combined results
        total_items = len(content_items)
        paginated_items = content_items[skip:skip + limit]
        
        return {
            "items": paginated_items,
            "total": total_items,
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total_items
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving content: {str(e)}"
        )

@router.get("/test")
async def test_discover(db: Session = Depends(get_db)):
    """Test endpoint to check database connectivity"""
    try:
        flashcard_count = db.query(func.count(Flashcard.id)).scalar()
        return {
            "status": "success",
            "flashcard_count": flashcard_count,
            "message": "Database connection working"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Database connection failed"
        }

@router.get("/trending")
async def get_trending_content(
    limit: int = Query(10, ge=1, le=50, description="Number of trending items to return"),
    db: Session = Depends(get_db)
):
    """
    Get trending content based on view count and recent activity.
    """
    try:
        # Get trending stories (by view count)
        trending_stories = db.query(Story).order_by(Story.view_count.desc(), Story.created_at.desc()).limit(limit).all()
        
        # Get recent content (last 7 days)
        recent_date = datetime.now() - timedelta(days=7)
        recent_flashcards = db.query(Flashcard).filter(Flashcard.created_at >= recent_date).order_by(Flashcard.created_at.desc()).limit(limit).all()
        recent_images = db.query(Image).filter(Image.created_at >= recent_date, Image.status == "completed").order_by(Image.created_at.desc()).limit(limit).all()
        
        # Combine and sort by creation date
        trending_items = []
        
        for story in trending_stories:
            trending_items.append({
                "id": story.id,
                "content_type": "story",
                "title": story.story_title,
                "target_language": story.target_language,
                "target_age_range": story.target_age_range,
                "view_count": story.view_count,
                "created_at": story.created_at.isoformat()
            })
        
        for flashcard in recent_flashcards:
            trending_items.append({
                "id": flashcard.id,
                "content_type": "flashcard",
                "title": flashcard.original_word,
                "target_language": flashcard.target_language,
                "created_at": flashcard.created_at.isoformat()
            })
        
        for image in recent_images:
            trending_items.append({
                "id": image.id,
                "content_type": "image",
                "title": image.original_word,
                "target_language": image.target_language,
                "image_url": image.image_url,
                "created_at": image.created_at.isoformat()
            })
        
        # Sort by creation date (newest first)
        trending_items.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {
            "trending_items": trending_items[:limit]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving trending content: {str(e)}"
        )

@router.get("/stats")
async def get_discovery_stats(db: Session = Depends(get_db)):
    """
    Get statistics about available content for discovery.
    """
    try:
        # Count content by type
        flashcard_count = db.query(func.count(Flashcard.id)).scalar()
        story_count = db.query(func.count(Story.id)).scalar()
        image_count = db.query(func.count(Image.id)).filter(Image.status == "completed").scalar()
        translation_count = db.query(func.count(Translation.id)).scalar()
        
        # Count by language
        language_stats = db.query(
            Flashcard.target_language,
            func.count(Flashcard.id).label("count")
        ).group_by(Flashcard.target_language).all()
        
        # Count by age group
        age_stats = db.query(
            Story.target_age_range,
            func.count(Story.id).label("count")
        ).filter(Story.target_age_range.isnot(None)).group_by(Story.target_age_range).all()
        
        return {
            "content_counts": {
                "flashcards": flashcard_count,
                "stories": story_count,
                "images": image_count,
                "translations": translation_count,
                "total": flashcard_count + story_count + image_count
            },
            "language_distribution": [
                {"language": lang, "count": count} for lang, count in language_stats
            ],
            "age_group_distribution": [
                {"age_group": age, "count": count} for age, count in age_stats
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving discovery stats: {str(e)}"
        ) 