from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"
    
    id = Column(String(128), primary_key=True)  # Firebase UID
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True))
    preferences = Column(JSONB)
    
    # Relationships
    flashcards = relationship("Flashcard", back_populates="user", cascade="all, delete-orphan")
    translations = relationship("Translation", back_populates="user", cascade="all, delete-orphan")
    stories = relationship("Story", back_populates="user", cascade="all, delete-orphan")
    images = relationship("Image", back_populates="user", cascade="all, delete-orphan")


class Flashcard(Base):
    __tablename__ = "flashcards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(128), ForeignKey("users.id"), nullable=False)
    original_word = Column(String(255), nullable=False)
    translated_word = Column(String(255), nullable=False)
    target_language = Column(String(50), nullable=False)  # e.g., "Spanish", "Chinese Simplified"
    example_sentences = Column(JSONB, nullable=False, server_default='[]')
    colors = Column(JSONB, nullable=False, server_default='{"primary": "#6690ff", "secondary": "#64748b"}')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now)
    
    # Relationships
    user = relationship("User", back_populates="flashcards")


class Translation(Base):
    __tablename__ = "translations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(128), ForeignKey("users.id"), nullable=False)
    original_term = Column(String(255), nullable=False)
    target_language = Column(String(10), nullable=False)
    translation = Column(Text, nullable=False)
    explanation = Column(Text)
    bookmarked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="translations")


class CachedTranslation(Base):
    __tablename__ = "cached_translations"
    
    id = Column(Integer, primary_key=True, index=True)
    prompt_hash = Column(String(64), unique=True, nullable=False, index=True)
    original_word = Column(String(255), nullable=False, index=True)
    target_language = Column(String(50), nullable=False, index=True)
    response_json = Column(JSONB, nullable=False)  # Store full LLM response


class Story(Base):
    __tablename__ = "stories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(128), ForeignKey("users.id"), nullable=False)
    original_words = Column(JSONB, nullable=False)  # Array of words used in story generation
    story_title = Column(String(255), nullable=False)
    story_content = Column(Text, nullable=False)
    story_theme = Column(String(100))
    story_length = Column(String(50))  # 'short', 'medium', 'long'
    target_age_range = Column(String(50))  # 'toddler', 'preschool', 'elementary', 'middle_school'
    target_language = Column(String(50))
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now)
    
    # Relationships
    user = relationship("User", back_populates="stories")


class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(128), ForeignKey("users.id"), nullable=False)
    original_word = Column(String(255), nullable=False)
    translated_word = Column(String(255), nullable=False)
    target_language = Column(String(50), nullable=False)
    image_url = Column(String(500))  # URL to the generated image
    generation_prompt = Column(Text, nullable=False)  # The prompt used for generation
    custom_instructions = Column(Text)  # Additional custom instructions
    status = Column(String(20), default="pending")  # 'pending', 'completed', 'failed'
    child_age = Column(Integer)  # Age used in generation
    title = Column(String(255))  # Optional title for the image
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now)
    
    # Relationships
    user = relationship("User", back_populates="images") 