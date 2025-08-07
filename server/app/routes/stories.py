from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Story
from ..schemas import Story as StorySchema, StoryCreate, StoryGenerationRequest
from ..crud import create_story, get_stories, get_story
import httpx
import os
import json

router = APIRouter(prefix="/stories", tags=["stories"])


@router.post("/generate")
async def generate_story(
    request: StoryGenerationRequest,
    db: Session = Depends(get_db)
):
    """Generate a story using Gemini 2.0 Flash API"""
    try:
        # Get Gemini API key from environment
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gemini API key not configured"
            )
        
        # Build the prompt for story generation
        words_text = ", ".join(request.words)
        base_prompt = f"""
        Create an engaging, educational story for children that incorporates the following words: {words_text}.
        
        Theme: {request.theme}
        Maximum length: {request.max_words} words
        Target audience: Elementary school children (ages 6-12)
        
        Requirements:
        - Make the story engaging and age-appropriate
        - Naturally incorporate all the provided words
        - Include educational elements or moral lessons
        - Use clear, simple language
        - Make it fun and memorable
        
        {f"Additional instructions: {request.custom_prompt}" if request.custom_prompt else ""}
        
        Please write the story in a clear, engaging format suitable for children.
        """
        
        # Call Gemini API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={gemini_api_key}",
                json={
                    "contents": [
                        {
                            "parts": [
                                {
                                    "text": base_prompt
                                }
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.7,
                        "topK": 40,
                        "topP": 0.95,
                        "maxOutputTokens": 1024
                    }
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate story from Gemini API"
                )
            
            data = response.json()
            
            # Extract the generated text
            if "candidates" in data and len(data["candidates"]) > 0:
                story_content = data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="No story content generated"
                )
        
        return {
            "story_content": story_content,
            "words": request.words,
            "theme": request.theme,
            "max_words": request.max_words
        }
        
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Story generation timed out"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Story generation failed: {str(e)}"
        )


@router.post("/", response_model=StorySchema)
async def create_story_endpoint(
    story_data: StoryCreate,
    db: Session = Depends(get_db)
):
    """Create a new story"""
    try:
        story = create_story(db, story_data)
        return story
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create story: {str(e)}"
        )


@router.get("/", response_model=List[StorySchema])
async def get_all_stories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all stories for discovery"""
    stories = get_stories(db, skip=skip, limit=limit)
    return stories


@router.get("/{story_id}", response_model=StorySchema)
async def get_story_by_id(
    story_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific story by ID"""
    story = get_story(db, story_id)
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    return story


@router.get("/discover", response_model=List[StorySchema])
async def discover_stories(
    theme: str = None,
    age_range: str = None,
    language: str = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Discover stories with optional filtering"""
    # This would implement filtering logic
    stories = get_stories(db, skip=skip, limit=limit)
    return stories 