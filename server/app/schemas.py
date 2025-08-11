from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


# User schemas
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    id: str  # Firebase UID


class User(UserBase):
    id: str
    created_at: datetime
    last_login_at: Optional[datetime] = None
    preferences: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


# User preferences schemas
class UserPreferences(BaseModel):
    child_name: Optional[str] = None
    child_age: Optional[int] = None
    preferred_languages: Optional[List[str]] = None
    content_privacy_default: Optional[str] = "private"


class UserPreferencesUpdate(BaseModel):
    preferences: Optional[UserPreferences] = None


class UserDelete(BaseModel):
    confirm_email: str  # User must type their email to confirm deletion


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


# Story schemas
class StoryBase(BaseModel):
    original_words: List[str]
    story_title: str
    story_content: str
    story_theme: Optional[str] = None
    story_length: Optional[str] = None  # 'short', 'medium', 'long'
    target_age_range: Optional[str] = None  # 'toddler', 'preschool', 'elementary', 'middle_school'
    target_language: Optional[str] = None


class StoryCreate(StoryBase):
    pass


class StoryUpdate(BaseModel):
    story_title: Optional[str] = None
    story_content: Optional[str] = None
    story_theme: Optional[str] = None
    story_length: Optional[str] = None
    target_age_range: Optional[str] = None
    target_language: Optional[str] = None


class Story(StoryBase):
    id: int
    user_id: str
    view_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class StoryGenerationRequest(BaseModel):
    words: List[str]
    theme: Optional[str] = None
    max_words: int = 100
    custom_prompt: Optional[str] = None
    target_language: Optional[str] = None
    age_range: Optional[str] = None
    original_word: Optional[str] = None
    translated_word: Optional[str] = None


# Image schemas
class ImageBase(BaseModel):
    original_word: str
    translated_word: str
    target_language: str
    generation_prompt: str
    custom_instructions: Optional[str] = None
    child_age: Optional[int] = None
    title: Optional[str] = None


class ImageCreate(ImageBase):
    pass


class ImageUpdate(BaseModel):
    title: Optional[str] = None
    custom_instructions: Optional[str] = None


class Image(ImageBase):
    id: int
    user_id: str
    image_url: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ImageGenerationRequest(BaseModel):
    original_word: str
    translated_word: str
    target_language: str
    custom_instructions: Optional[str] = None
    child_age: Optional[int] = None
    title: Optional[str] = None 