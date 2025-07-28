from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(String(128), primary_key=True)  # Firebase UID
    email = Column(String(255), unique=True, nullable=False)
    display_name = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True))
    preferences = Column(JSONB)
    
    # Relationships
    flashcards = relationship("Flashcard", back_populates="user", cascade="all, delete-orphan")
    translations = relationship("Translation", back_populates="user", cascade="all, delete-orphan")


class Flashcard(Base):
    __tablename__ = "flashcards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(128), ForeignKey("users.id"), nullable=False)
    original_word = Column(String(255), nullable=False)
    translated_word = Column(String(255), nullable=False)
    example_sentences = Column(JSONB)  # Array of example sentences
    template = Column(String(50), default="classic")
    colors = Column(JSONB)  # Store color scheme as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
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