from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    display_name: Optional[str] = None


class UserCreate(UserBase):
    id: str  # Firebase UID


class User(UserBase):
    id: str
    created_at: datetime
    last_login_at: Optional[datetime] = None
    preferences: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


# Flashcard schemas
class FlashcardBase(BaseModel):
    original_word: str
    translated_word: str
    target_language: str
    example_sentences: List[str] = []
    colors: Dict[str, str] = {"primary": "#6690ff", "secondary": "#64748b"}


class FlashcardCreate(FlashcardBase):
    pass


class FlashcardUpdate(BaseModel):
    original_word: Optional[str] = None
    translated_word: Optional[str] = None
    target_language: Optional[str] = None
    example_sentences: Optional[List[str]] = None
    colors: Optional[Dict[str, str]] = None


class Flashcard(FlashcardBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Translation schemas
class TranslationBase(BaseModel):
    original_term: str
    target_language: str
    translation: str
    explanation: Optional[str] = None
    bookmarked: bool = False


class TranslationCreate(TranslationBase):
    pass


class Translation(TranslationBase):
    id: int
    user_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Authentication schemas
class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    display_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Flashcard preview schema
class FlashcardPreview(BaseModel):
    original_word: str
    translated_word: str
    example_sentences: Optional[List[str]] = None
    colors: Optional[Dict[str, str]] = None


# Word management schemas
class WordSummary(BaseModel):
    original_word: str
    target_language: str
    translation: str
    explanation: Optional[str] = None
    examples: Optional[List[str]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True 