from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os
import json
import re
from dotenv import load_dotenv
from ..secrets import get_gemini_api_key

load_dotenv()

router = APIRouter(tags=["translate"])

class TranslateRequest(BaseModel):
    term: str
    language: str

class TranslateResponse(BaseModel):
    translation: str
    explanation: str

@router.post("/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    """Translate a term using Gemini API"""
    try:
        # Get Gemini API key from Secret Manager or environment
        api_key = get_gemini_api_key()
        environment = os.getenv("ENVIRONMENT", "local")
        
        # Check if we have a valid API key
        if not api_key or api_key == "your_gemini_api_key_here":
            # For local development without API key, return mock response
            return TranslateResponse(
                translation=f"[{request.language}] {request.term}",
                explanation=f"This is a mock translation for '{request.term}' to {request.language}. To use real translations, set GEMINI_API_KEY in your environment or add the secret to Secret Manager."
            )
        
        # Prepare the prompt for Gemini
        prompt = f"""
        Translate the word or phrase "{request.term}" to {request.language}.
        
        Please provide your response in the following JSON format:
        {{
            "translation": "the translated word or phrase",
            "explanation": "a brief explanation of the translation, including any cultural context, usage notes, or grammar explanations"
        }}
        
        Make sure the explanation is helpful for language learners and includes:
        - Pronunciation hints if relevant
        - Common usage examples
        - Any cultural context
        - Grammar notes if applicable
        
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
                    explanation=f"Translation service temporarily unavailable. This is a fallback response for '{request.term}' to {request.language}."
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
                        
                        return TranslateResponse(
                            translation=parsed.get("translation", "Translation not available"),
                            explanation=parsed.get("explanation", "Explanation not available")
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
                            explanation=explanation
                        )
            
            # Fallback if response format is unexpected
            print(f"Unexpected Gemini response format: {data}")
            return TranslateResponse(
                translation=f"[{request.language}] {request.term}",
                explanation=f"Unexpected response format from translation service. This is a fallback for '{request.term}' to {request.language}."
            )
            
    except httpx.TimeoutException:
        print("Gemini API request timed out")
        return TranslateResponse(
            translation=f"[{request.language}] {request.term}",
            explanation=f"Translation request timed out. This is a fallback response for '{request.term}' to {request.language}."
        )
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return TranslateResponse(
            translation=f"[{request.language}] {request.term}",
            explanation=f"Translation service error: {str(e)}. This is a fallback response for '{request.term}' to {request.language}."
        ) 