from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

class TranslateRequest(BaseModel):
    term: str

@app.post("/api/translate")
async def translate(req: TranslateRequest):
    # Dummy translation logic
    return {"term": req.term, "translation": f"{req.term} (translated)"} 