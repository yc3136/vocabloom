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
        email=user.email,
        display_name=user.display_name
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
    return None 