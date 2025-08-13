from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from ..database import get_db
from ..models import Story
from ..schemas import Story as StorySchema, StoryCreate, StoryGenerationRequest
from ..crud import create_story, get_stories, get_story, delete_story
from ..auth import get_current_user
from ..models import User
from ..redis_quota import check_and_increment_quota, check_quota_only, get_remaining_quota, has_pending_generation, start_generation, end_generation
import httpx
import os
import json

router = APIRouter(prefix="/stories", tags=["stories"])


@router.post("/generate")
async def generate_story(
    request: StoryGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a story using Gemini 2.0 Flash API"""
    try:
        # Check if user has pending generations
        if has_pending_generation(current_user.id, 'story'):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="You already have a story generation in progress. Please wait for it to complete before starting another one."
            )
        
        # Check quota before starting generation
        if not check_quota_only(current_user.id, 'story'):
            quota_info = get_remaining_quota(current_user.id, 'story')
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Daily story generation limit reached. You have used {quota_info['used']}/{quota_info['limit']} stories today. Please try again tomorrow."
            )
        
        # Mark generation as started
        start_generation(current_user.id, 'story')
        
        # Increment quota now that we're starting generation
        check_and_increment_quota(current_user.id, 'story')
        
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
        if request.target_language and request.target_language != "None" and request.target_language.strip():
            language_instruction = f"IMPORTANT: Write the entire story in {request.target_language} language. Do not use English unless specifically requested. "
        else:
            language_instruction = "Write the story in English. "
        
        # Word highlighting instruction
        word_highlighting = ""
        if request.words and len(request.words) > 0:
            # Highlight all selected words
            words_to_highlight = request.words
            word_highlighting = f"""
        Word Usage:
        - Include and highlight ALL of these words: {', '.join(words_to_highlight)}
        - Make each word **bold** when it appears (use **word** format)
        - Ensure each word appears multiple times throughout the story
        - The story should be written in {request.target_language} language
        - Use the words naturally in the story context
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
        
        CRITICAL LANGUAGE REQUIREMENTS:
        - Write the story ENTIRELY in {request.target_language} language
        - NEVER include pinyin, romanization, or pronunciation guides in parentheses
        - NEVER add English translations or explanations
        - NEVER use English words or phrases
        - Use ONLY the target language characters and words
        
        Story Requirements:
        - Make the story engaging and age-appropriate
        - Naturally incorporate all the provided words
        - Include educational elements or moral lessons
        - Use {age_guidance}
        - Make it fun and memorable
        - Keep the story within {request.max_words} words
        {word_highlighting}
        
        {f"Additional instructions: {request.custom_prompt}" if request.custom_prompt else ""}
        
        IMPORTANT: The story must be written in pure {request.target_language} without any pronunciation guides, pinyin, or English text.
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
        
        # Quota was already incremented at the start, no need to increment again
        
        # Mark generation as ended
        end_generation(current_user.id, 'story')
        
        return {
            "story_content": story_content,
            "words": request.words,
            "theme": request.theme,
            "max_words": request.max_words,
            "target_language": request.target_language,
            "age_range": request.age_range
        }
        
    except httpx.TimeoutException:
        # Mark generation as ended
        end_generation(current_user.id, 'story')
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Story generation timed out"
        )
    except HTTPException:
        # Mark generation as ended
        end_generation(current_user.id, 'story')
        # Re-raise HTTP exceptions (like quota limits) without modification
        raise
    except Exception as e:
        # Mark generation as ended
        end_generation(current_user.id, 'story')
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


class RelatedWordsRequest(BaseModel):
    word: str
    target_language: str
    max_words: int = 8
    child_age: Optional[int] = None


@router.post("/related-words")
async def get_related_words(
    request: RelatedWordsRequest,
    db: Session = Depends(get_db)
):
    """Generate related words for story creation using AI"""
    try:
        # Get Gemini API key from environment
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gemini API key not configured"
            )
        
        # Determine age-appropriate guidance
        age_guidance = ""
        if request.child_age:
            if request.child_age <= 3:
                age_guidance = "Use very simple, basic words that toddlers can understand. Focus on concrete objects, simple actions, and familiar concepts. Avoid abstract or complex words."
            elif request.child_age <= 5:
                age_guidance = "Use simple, concrete words that preschoolers can grasp. Include basic colors, shapes, animals, and everyday objects. Keep vocabulary accessible and familiar."
            elif request.child_age <= 8:
                age_guidance = "Use age-appropriate words that elementary school children can understand. Include some educational concepts, descriptive words, and slightly more complex vocabulary."
            elif request.child_age <= 12:
                age_guidance = "Use words suitable for older children. Can include more descriptive language, abstract concepts, and educational vocabulary while remaining age-appropriate."
            else:
                age_guidance = "Use age-appropriate vocabulary suitable for children. Focus on clear, understandable words that support learning."
        else:
            age_guidance = "Use age-appropriate vocabulary suitable for children. Focus on clear, understandable words that support learning."

        # Build the prompt for related words generation
        prompt = f"""
        You are a language learning assistant. Generate exactly {request.max_words} contextually specific words for the word "{request.word}" in {request.target_language} language.

        AGE GUIDANCE: {age_guidance}

        CRITICAL REQUIREMENTS:
        - Each word must be SPECIFICALLY related to "{request.word}" and its context
        - Choose words appropriate for a {request.child_age if request.child_age else 'child'} year old
        - Avoid generic words like "happy", "friend", "big", "small" unless they are truly specific to "{request.word}"
        - Choose words that would naturally appear in a story specifically about "{request.word}"
        - Include words that are part of the same semantic field or scenario
        - Focus on words that create a coherent story about "{request.word}"
        - Ensure all words are age-appropriate and educational

        Examples for different words (age-appropriate):
        - For "sun" (toddler): bright, hot, yellow, sky, day, warm, shine, light
        - For "dog" (preschool): bark, tail, pet, walk, bone, play, furry, friend
        - For "tree" (elementary): leaf, branch, grow, green, tall, forest, nature, plant
        - For "book" (older child): read, story, page, learn, library, knowledge, words, imagination
        - For "yellow" (preschool): color, bright, sunshine, flower, paint, lemon, banana, golden
        - For "blue" (elementary): sky, ocean, water, cool, calm, sea, azure, cerulean

        RESPONSE FORMAT - YOU MUST RETURN ONLY VALID JSON:
        [
          {{"english": "word1", "translation": "translation1"}},
          {{"english": "word2", "translation": "translation2"}},
          {{"english": "word3", "translation": "translation3"}},
          {{"english": "word4", "translation": "translation4"}}
        ]

        CRITICAL: 
        - Return ONLY the JSON array above
        - Do NOT include any explanations, markdown formatting, or additional text
        - Ensure the JSON is properly formatted with double quotes
        - Make sure the array contains exactly {request.max_words} items
        - Each item must have "english" and "translation" fields
        - Choose words appropriate for a {request.child_age if request.child_age else 'child'} year old
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
                                    "text": prompt
                                }
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.7,
                        "topK": 40,
                        "topP": 0.95,
                        "maxOutputTokens": 512
                    }
                },
                timeout=15.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate related words from Gemini API"
                )
            
            data = response.json()
            
            # Extract the generated text
            if "candidates" in data and len(data["candidates"]) > 0:
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                print(f"AI Response for related words: {content}")
                
                # Parse the JSON response
                try:
                    import json
                    related_words = json.loads(content.strip())
                    
                    # Validate the structure
                    if not isinstance(related_words, list):
                        raise ValueError("Response is not a list")
                    
                    # Ensure each item has the required fields
                    validated_words = []
                    for word in related_words:
                        if isinstance(word, dict) and "english" in word and "translation" in word:
                            validated_words.append({
                                "id": f"{word['english']}_{word['translation']}",
                                "english": word["english"],
                                "translation": word["translation"]
                            })
                    
                    print(f"Successfully parsed {len(validated_words)} related words")
                    return {"related_words": validated_words}
                    
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"JSON parsing failed for word '{request.word}': {e}")
                    print(f"Raw AI response: {repr(content)}")
                    print(f"Response length: {len(content)}")
                    
                    # Try to extract JSON from the response if it's wrapped in other text
                    import re
                    json_match = re.search(r'\[.*\]', content, re.DOTALL)
                    if json_match:
                        try:
                            extracted_json = json_match.group(0)
                            print(f"Extracted JSON: {extracted_json}")
                            related_words = json.loads(extracted_json)
                            if isinstance(related_words, list):
                                validated_words = []
                                for word in related_words:
                                    if isinstance(word, dict) and "english" in word and "translation" in word:
                                        validated_words.append({
                                            "id": f"{word['english']}_{word['translation']}",
                                            "english": word["english"],
                                            "translation": word["translation"]
                                        })
                                print(f"Successfully parsed {len(validated_words)} words from extracted JSON")
                                return {"related_words": validated_words}
                        except Exception as extract_error:
                            print(f"Failed to parse extracted JSON: {extract_error}")
                    
                    # Fallback: return some basic related words
                    fallback_words = [
                        {"id": "friend_朋友", "english": "friend", "translation": "朋友"},
                        {"id": "happy_快乐", "english": "happy", "translation": "快乐"},
                        {"id": "big_大", "english": "big", "translation": "大"},
                        {"id": "small_小", "english": "small", "translation": "小"}
                    ]
                    print(f"Using fallback words for '{request.word}'")
                    return {"related_words": fallback_words}
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="No related words generated"
                )
        
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Related words generation timed out"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Related words generation failed: {str(e)}"
        ) 