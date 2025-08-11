from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional
from datetime import datetime


# User CRUD operations
def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        id=user.id,
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_last_login(db: Session, user_id: str):
    user = get_user(db, user_id)
    if user:
        user.last_login_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
    return user


def update_user_preferences(db: Session, user_id: str, preferences: Optional[dict] = None):
    user = get_user(db, user_id)
    if user:
        if preferences is not None:
            user.preferences = preferences
        db.commit()
        db.refresh(user)
    return user


def delete_user_account(db: Session, user_id: str):
    """Delete user account and all associated data"""
    user = get_user(db, user_id)
    if user:
        # Delete all user data (flashcards and translations will be deleted via cascade)
        db.delete(user)
        db.commit()
        return True
    return False


# Flashcard CRUD operations
def get_flashcards(db: Session, user_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.Flashcard).filter(
        models.Flashcard.user_id == user_id
    ).order_by(models.Flashcard.created_at.desc()).offset(skip).limit(limit).all()


def get_flashcard(db: Session, flashcard_id: int, user_id: str):
    return db.query(models.Flashcard).filter(
        models.Flashcard.id == flashcard_id,
        models.Flashcard.user_id == user_id
    ).first()


def create_flashcard(db: Session, flashcard: schemas.FlashcardCreate, user_id: str):
    db_flashcard = models.Flashcard(
        **flashcard.dict(),
        user_id=user_id
    )
    db.add(db_flashcard)
    db.commit()
    db.refresh(db_flashcard)
    return db_flashcard


def update_flashcard(db: Session, flashcard_id: int, flashcard: schemas.FlashcardUpdate, user_id: str):
    db_flashcard = get_flashcard(db, flashcard_id, user_id)
    if not db_flashcard:
        return None
    
    update_data = flashcard.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_flashcard, field, value)
    
    db.commit()
    db.refresh(db_flashcard)
    return db_flashcard


def delete_flashcard(db: Session, flashcard_id: int, user_id: str):
    db_flashcard = get_flashcard(db, flashcard_id, user_id)
    if db_flashcard:
        db.delete(db_flashcard)
        db.commit()
        return True
    return False


# Translation CRUD operations
def get_translations(db: Session, user_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.Translation).filter(
        models.Translation.user_id == user_id
    ).order_by(models.Translation.created_at.desc()).offset(skip).limit(limit).all()


def get_translation(db: Session, translation_id: int, user_id: str):
    return db.query(models.Translation).filter(
        models.Translation.id == translation_id,
        models.Translation.user_id == user_id
    ).first()


def create_translation(db: Session, translation: schemas.TranslationCreate, user_id: str):
    db_translation = models.Translation(
        **translation.dict(),
        user_id=user_id
    )
    db.add(db_translation)
    db.commit()
    db.refresh(db_translation)
    return db_translation


def update_translation_bookmark(db: Session, translation_id: int, user_id: str, bookmarked: bool):
    db_translation = get_translation(db, translation_id, user_id)
    if db_translation:
        db_translation.bookmarked = bookmarked
        db.commit()
        db.refresh(db_translation)
    return db_translation


# Story CRUD operations
def get_stories(db: Session, skip: int = 0, limit: int = 100, user_id: Optional[str] = None):
    query = db.query(models.Story)
    if user_id:
        query = query.filter(models.Story.user_id == user_id)
    return query.order_by(models.Story.created_at.desc()).offset(skip).limit(limit).all()


def get_story(db: Session, story_id: int, user_id: Optional[str] = None):
    query = db.query(models.Story).filter(models.Story.id == story_id)
    if user_id:
        query = query.filter(models.Story.user_id == user_id)
    return query.first()


def create_story(db: Session, story_data: dict):
    db_story = models.Story(**story_data)
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    return db_story


def update_story(db: Session, story_id: int, story: schemas.StoryUpdate, user_id: Optional[str] = None):
    db_story = get_story(db, story_id, user_id)
    if not db_story:
        return None
    
    update_data = story.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_story, field, value)
    
    db.commit()
    db.refresh(db_story)
    return db_story


def delete_story(db: Session, story_id: int, user_id: Optional[str] = None):
    db_story = get_story(db, story_id, user_id)
    if db_story:
        db.delete(db_story)
        db.commit()
        return True
    return False


def increment_story_view_count(db: Session, story_id: int):
    story = db.query(models.Story).filter(models.Story.id == story_id).first()
    if story:
        story.view_count += 1
        db.commit()
        db.refresh(story)
    return story


# Image CRUD operations
def get_images(db: Session, user_id: str, skip: int = 0, limit: int = 100):
    return db.query(models.Image).filter(
        models.Image.user_id == user_id
    ).order_by(models.Image.created_at.desc()).offset(skip).limit(limit).all()


def get_image(db: Session, image_id: int, user_id: str):
    return db.query(models.Image).filter(
        models.Image.id == image_id,
        models.Image.user_id == user_id
    ).first()


def create_image(db: Session, image: schemas.ImageCreate, user_id: str):
    db_image = models.Image(
        **image.dict(),
        user_id=user_id
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


def update_image(db: Session, image_id: int, image: schemas.ImageUpdate, user_id: str):
    db_image = get_image(db, image_id, user_id)
    if not db_image:
        return None
    
    update_data = image.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_image, field, value)
    
    db.commit()
    db.refresh(db_image)
    return db_image


def update_image_status(db: Session, image_id: int, status: str, image_url: Optional[str] = None):
    """Update image status and optionally set the image URL when generation is complete"""
    image = db.query(models.Image).filter(models.Image.id == image_id).first()
    if image:
        image.status = status
        if image_url:
            image.image_url = image_url
        image.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(image)
    return image


def delete_image(db: Session, image_id: int, user_id: str) -> bool:
    """Delete an image and its file from Google Cloud Storage"""
    image = db.query(models.Image).filter(models.Image.id == image_id, models.Image.user_id == user_id).first()
    if image:
        # Delete from Google Cloud Storage if URL exists
        if image.image_url:
            try:
                from app.storage import storage_manager
                # Extract filename from URL
                filename = image.image_url.split('/')[-1]
                storage_manager.delete_image(filename)
            except Exception as e:
                print(f"Error deleting image from GCS: {e}")
                # Continue with database deletion even if GCS deletion fails
        
        db.delete(image)
        db.commit()
        return True
    return False 