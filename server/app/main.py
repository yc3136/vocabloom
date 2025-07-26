from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import httpx
from google.cloud import secretmanager
import json

app = FastAPI(title="Vocabloom API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative dev port
        "https://vocabloom-467020.web.app",  # Firebase Hosting
        "https://vocabloom-467020.firebaseapp.com",  # Firebase Hosting alternative
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranslationRequest(BaseModel):
    term: str
    language: str

class TranslationResponse(BaseModel):
    translation: str
    explanation: str

# Initialize Secret Manager client (only in production)
secret_client = None
if os.getenv("GOOGLE_CLOUD_PROJECT"):
    secret_client = secretmanager.SecretManagerServiceClient()

def get_gemini_api_key():
    """Get Gemini API key from Secret Manager or environment variable"""
    # For local development, use environment variable
    if not secret_client:
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            return api_key
        else:
            print("Warning: GEMINI_API_KEY environment variable not set for local development")
            return None
    
    # For production, use Secret Manager
    try:
        name = f"projects/vocabloom-467020/secrets/gemini-api-key/versions/latest"
        response = secret_client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"Error accessing secret: {e}")
        return None

async def call_gemini_api(term: str, language: str) -> dict:
    """Call Gemini API for translation and explanation"""
    api_key = get_gemini_api_key()
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not available")
    
    # Gemini API endpoint - using Gemini 2.0 Flash
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    # Create a comprehensive prompt for translation and explanation
    prompt = f"""
    Please help translate and explain the English term "{term}" to {language}.
    
    Provide your response in JSON format with two fields:
    1. "translation": The accurate translation of the term
    2. "explanation": A clear, educational explanation of what this term means in {language}, suitable for language learners
    
    Make the explanation helpful for someone learning {language}, including cultural context if relevant.
    """
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=30.0)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract the response text from Gemini
            if "candidates" in data and len(data["candidates"]) > 0:
                response_text = data["candidates"][0]["content"]["parts"][0]["text"]
                
                # Try to parse as JSON, fallback to text processing
                try:
                    result = json.loads(response_text)
                    return {
                        "translation": result.get("translation", f"Translation of '{term}'"),
                        "explanation": result.get("explanation", f"Explanation of '{term}' in {language}")
                    }
                except json.JSONDecodeError:
                    # If not JSON, split the response
                    lines = response_text.strip().split('\n')
                    translation = lines[0] if lines else f"Translation of '{term}'"
                    explanation = '\n'.join(lines[1:]) if len(lines) > 1 else f"Explanation of '{term}' in {language}"
                    return {"translation": translation, "explanation": explanation}
            else:
                raise HTTPException(status_code=500, detail="Invalid response from Gemini API")
                
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {e.response.text}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Vocabloom API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "vocabloom-api"}

@app.post("/api/translate", response_model=TranslationResponse)
async def translate_term(request: TranslationRequest):
    """
    Translate a term using Gemini API
    """
    try:
        # Validate input
        if not request.term.strip():
            raise HTTPException(status_code=400, detail="Term cannot be empty")
        
        if not request.language.strip():
            raise HTTPException(status_code=400, detail="Language cannot be empty")
        
        # Call Gemini API for translation and explanation
        result = await call_gemini_api(request.term.strip(), request.language.strip())
        
        return TranslationResponse(
            translation=result["translation"],
            explanation=result["explanation"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
