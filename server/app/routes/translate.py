from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import httpx
import os
import json
import re
from typing import Optional
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from ..secrets import get_gemini_api_key
from ..database import get_db
from ..caching import hash_prompt, get_cached_translation, cache_translation
from ..auth import get_current_user_if_authenticated
from ..models import Translation, User

load_dotenv()

def get_age_appropriate_examples(term: str, language: str, child_age: Optional[int] = None) -> list[str]:
    """Generate age-appropriate example sentences based on child's age."""
    if not child_age:
        return [
            f"Example 1: I learned the word '{term}' in {language} class.",
            f"Example 2: Can you say '{term}' in {language}?",
            f"Example 3: The word '{term}' means something special in {language}."
        ]
    
    if child_age <= 5:
        return [
            f"Look! A {term}!",
            f"Can you point to the {term}?",
            f"The {term} is so pretty!"
        ]
    elif child_age <= 8:
        return [
            f"I see a {term} in the picture.",
            f"Let's learn about {term} today!",
            f"The {term} is my favorite."
        ]
    elif child_age <= 12:
        return [
            f"I learned about {term} in school today.",
            f"Can you tell me more about {term}?",
            f"The {term} is really interesting!"
        ]
    else:
        return [
            f"Example 1: I learned the word '{term}' in {language} class.",
            f"Example 2: Can you say '{term}' in {language}?",
            f"Example 3: The word '{term}' means something special in {language}."
        ]

router = APIRouter(tags=["translate"])

class TranslateRequest(BaseModel):
    term: str
    language: str
    child_age: Optional[int] = None

class TranslateResponse(BaseModel):
    translation: str
    explanation: str
    examples: list[str]
    cached: bool = False
    cache_hit_count: Optional[int] = None

@router.post("/translate", response_model=TranslateResponse)
async def translate(
    request: TranslateRequest, 
    current_user: Optional[User] = Depends(get_current_user_if_authenticated),
    db: Session = Depends(get_db)
):
    """Translate a term using Gemini API with caching"""
    try:
        # Get user preferences for age-appropriate caching
        user_preferences = None
        if current_user and current_user.preferences:
            user_preferences = current_user.preferences
        
        # Check cache first (works for all users)
        prompt_hash = hash_prompt(request.term, request.language, user_preferences)
        cached_result = get_cached_translation(db, prompt_hash)
        
        if cached_result:
            # Return cached result
            cached_data = cached_result.response_json
            return TranslateResponse(
                translation=cached_data.get("translation", "Translation not available"),
                explanation=cached_data.get("explanation", "Explanation not available"),
                examples=cached_data.get("examples", []),
                cached=True,
                cache_hit_count=None  # No longer tracking usage count
            )
        
        # Get Gemini API key from Secret Manager or environment
        api_key = get_gemini_api_key()
        environment = os.getenv("ENVIRONMENT", "local")
        
        # Check if we have a valid API key
        if not api_key or api_key == "your_gemini_api_key_here":
            # For local development without API key, return mock response
            return TranslateResponse(
                translation=f"[{request.language}] {request.term}",
                explanation=f"This is a mock translation for '{request.term}' to {request.language}. To use real translations, set GEMINI_API_KEY in your environment or add the secret to Secret Manager.",
                examples=get_age_appropriate_examples(request.term, request.language, request.child_age),
                cached=False,
                cache_hit_count=None
            )
        
        # Get user's child age for age-appropriate examples
        child_age_info = ""
        if request.child_age:
            child_age_info = f"\nThe examples should be appropriate for a {request.child_age}-year-old child. Use simple vocabulary and concepts that a {request.child_age}-year-old would understand and find engaging."
        
        # Prepare the prompt for Gemini
        prompt = f"""
        Translate the word or phrase "{request.term}" to {request.language}.
        
        Please provide your response in the following JSON format:
        {{
            "translation": "the translated word or phrase",
            "explanation": "a brief explanation of the translation, including any cultural context, usage notes, or grammar explanations",
            "examples": [
                "example sentence 1 using the word/phrase",
                "example sentence 2 using the word/phrase",
                "example sentence 3 using the word/phrase"
            ]
        }}
        
        Make sure the explanation is helpful for language learners and includes:
        - Pronunciation hints if relevant
        - Common usage examples
        - Any cultural context
        - Grammar notes if applicable
        
        For the examples, generate 3 simple example sentences that a kid would understand. Make them engaging and educational.{child_age_info}
        
        Respond only with valid JSON, no additional text.
        """
        
        # Call Gemini API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
                params={"key": api_key},
                json={
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }]
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                print(f"Gemini API error: {response.status_code} - {response.text}")
                # Fallback to mock response on API error
                return TranslateResponse(
                    translation=f"[{request.language}] {request.term}",
                    explanation=f"Translation service temporarily unavailable. This is a fallback response for '{request.term}' to {request.language}.",
                    examples=get_age_appropriate_examples(request.term, request.language, request.child_age),
                    cached=False,
                    cache_hit_count=None
                )
            
            data = response.json()
            
            # Extract the response text
            if "candidates" in data and len(data["candidates"]) > 0:
                content = data["candidates"][0]["content"]
                if "parts" in content and len(content["parts"]) > 0:
                    response_text = content["parts"][0]["text"].strip()
                    
                    # Try to parse JSON response
                    try:
                        # First, try to extract JSON from markdown code blocks
                        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                        if json_match:
                            json_str = json_match.group(1)
                            parsed = json.loads(json_str)
                        else:
                            # Try direct JSON parsing
                            parsed = json.loads(response_text)
                        
                        # Cache the successful response
                        cache_translation(
                            db=db,
                            prompt_hash=prompt_hash,
                            word=request.term,
                            language=request.language,
                            response_data=parsed
                        )
                        
                        # Save translation to user's history if authenticated
                        if current_user:
                            translation = Translation(
                                user_id=current_user.id,
                                original_term=request.term,
                                target_language=request.language,
                                translation=parsed.get("translation", "Translation not available"),
                                explanation=parsed.get("explanation", "Explanation not available")
                            )
                            db.add(translation)
                            db.commit()
                        
                        return TranslateResponse(
                            translation=parsed.get("translation", "Translation not available"),
                            explanation=parsed.get("explanation", "Explanation not available"),
                            examples=parsed.get("examples", []),
                            cached=False,
                            cache_hit_count=None
                        )
                    except json.JSONDecodeError:
                        # If JSON parsing fails, try to extract translation from text
                        print(f"JSON parsing failed for response: {response_text}")
                        # Look for translation pattern in the response
                        lines = response_text.split('\n')
                        translation = f"[{request.language}] {request.term}"
                        explanation = response_text
                        
                        # Try to find translation in the response
                        for line in lines:
                            if 'translation' in line.lower() and ':' in line:
                                translation = line.split(':', 1)[1].strip().strip('"')
                                break
                        
                        return TranslateResponse(
                            translation=translation,
                            explanation=explanation,
                            examples=get_age_appropriate_examples(request.term, request.language, request.child_age),
                            cached=False,
                            cache_hit_count=None
                        )
            
            # Fallback if response format is unexpected
            print(f"Unexpected Gemini response format: {data}")
            return TranslateResponse(
                translation=f"[{request.language}] {request.term}",
                explanation=f"Unexpected response format from translation service. This is a fallback for '{request.term}' to {request.language}.",
                examples=get_age_appropriate_examples(request.term, request.language, request.child_age),
                cached=False,
                cache_hit_count=None
            )
            
    except httpx.TimeoutException:
        print("Gemini API request timed out")
        return TranslateResponse(
            translation=f"[{request.language}] {request.term}",
            explanation=f"Translation request timed out. This is a fallback response for '{request.term}' to {request.language}.",
            examples=get_age_appropriate_examples(request.term, request.language, request.child_age),
            cached=False,
            cache_hit_count=None
        )
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return TranslateResponse(
            translation=f"[{request.language}] {request.term}",
            explanation=f"Translation service error: {str(e)}. This is a fallback response for '{request.term}' to {request.language}.",
            examples=get_age_appropriate_examples(request.term, request.language, request.child_age),
            cached=False,
            cache_hit_count=None
        ) 