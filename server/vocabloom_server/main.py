from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

class TranslateRequest(BaseModel):
    term: str

@app.post("/api/translate")
async def translate(req: TranslateRequest):
    return {"message": f"received translation request for {req.term}"} 