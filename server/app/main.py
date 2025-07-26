from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

app = FastAPI(title="Vocabloom API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
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
        # TODO: Integrate with Gemini API
        # For now, return a placeholder response
        return TranslationResponse(
            translation=f"Translation of '{request.term}' to {request.language}",
            explanation=f"Explanation of '{request.term}' in {request.language}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
