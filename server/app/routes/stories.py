from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Story
from ..schemas import Story as StorySchema, StoryCreate, StoryGenerationRequest
from ..crud import create_story, get_stories, get_story, delete_story
from ..auth import get_current_user
from ..models import User
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
        # Validate required fields
        if not request.words or len(request.words) == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="At least one word is required for story generation"
            )
        
        # Log the request for debugging
        print(f"Story generation request: words={request.words}, theme={request.theme}, max_words={request.max_words}")
        
        # Get Gemini API key from environment
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gemini API key not configured"
            )
        
        # Build the prompt for story generation
        words_text = ", ".join(request.words)
        
        # Determine age-appropriate content based on age_range
        age_guidance = ""
        if request.age_range:
            if request.age_range == "toddler" or (isinstance(request.age_range, int) and request.age_range <= 3):
                age_guidance = "very simple language, repetitive patterns, basic concepts, 1-2 sentences per page"
            elif request.age_range == "preschool" or (isinstance(request.age_range, int) and 4 <= request.age_range <= 5):
                age_guidance = "simple language, colorful descriptions, basic vocabulary, short sentences"
            elif request.age_range == "elementary" or (isinstance(request.age_range, int) and 6 <= request.age_range <= 10):
                age_guidance = "engaging language, educational elements, clear plot, age-appropriate themes"
            elif request.age_range == "middle_school" or (isinstance(request.age_range, int) and 11 <= request.age_range <= 13):
                age_guidance = "more complex language, deeper themes, character development, educational content"
            else:
                age_guidance = "engaging language suitable for children, educational elements, clear plot"
        else:
            age_guidance = "engaging language suitable for children, educational elements, clear plot"
        
        # Language instruction
        language_instruction = ""
        if request.target_language:
            language_instruction = f"Write the story in {request.target_language} language. "
        
        # Word highlighting instruction
        word_highlighting = ""
        if request.original_word and request.translated_word:
            word_highlighting = f"""
        Word Usage:
        - Include the original word "{request.original_word}" in the story context
        - Use the translated word "{request.translated_word}" prominently in the target language
        - Highlight the translated word by making it stand out (use **bold** or emphasize it naturally)
        - Ensure the translated word appears multiple times throughout the story
        """
        
        # Theme instruction - let AI be creative if no theme specified
        theme_instruction = ""
        if request.theme and request.theme.strip():
            theme_instruction = f"Theme: {request.theme}\n"
        else:
            theme_instruction = "Theme: Be creative and choose an engaging theme that fits the words naturally.\n"
        
        base_prompt = f"""
        {language_instruction}Create an engaging, educational story for children that incorporates the following words: {words_text}.
        
        {theme_instruction}Maximum length: {request.max_words} words
        Age guidance: {age_guidance}
        
        Requirements:
        - Make the story engaging and age-appropriate
        - Naturally incorporate all the provided words
        - Include educational elements or moral lessons
        - Use {age_guidance}
        - Make it fun and memorable
        - Keep the story within {request.max_words} words
        {word_highlighting}
        
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
            "max_words": request.max_words,
            "target_language": request.target_language,
            "age_range": request.age_range
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new story for the authenticated user"""
    try:
        # Add user_id to the story data
        story_data_dict = story_data.dict()
        story_data_dict["user_id"] = current_user.id
        
        story = create_story(db, story_data_dict)
        return story
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create story: {str(e)}"
        )


@router.get("/", response_model=List[StorySchema])
async def get_user_stories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all stories for the authenticated user"""
    stories = get_stories(db, skip=skip, limit=limit, user_id=current_user.id)
    return stories


@router.get("/{story_id}", response_model=StorySchema)
async def get_story_by_id(
    story_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific story by ID for the authenticated user"""
    story = get_story(db, story_id, user_id=current_user.id)
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    return story


@router.delete("/{story_id}")
async def delete_story_endpoint(
    story_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a story for the authenticated user"""
    success = delete_story(db, story_id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found"
        )
    return {"message": "Story deleted successfully"}


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