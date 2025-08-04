from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from app.database import engine, Base
from app.auth import initialize_firebase
from app.routes import auth, flashcards, translations, translate, cache, words

# Initialize FastAPI app
app = FastAPI(
    title="Vocabloom API",
    description="AI-powered language learning platform API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://localhost:5174",
        "https://vocabloom.app",
        "https://www.vocabloom.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase (always uses Secret Manager)
print("Initializing Firebase using Secret Manager")
initialize_firebase()

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Warning: Could not create database tables: {e}")
        print("This is normal for local development without PostgreSQL")

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(flashcards.router, prefix="/api")
app.include_router(translations.router, prefix="/api")
app.include_router(translate.router, prefix="/api")
app.include_router(cache.router, prefix="/api")
app.include_router(words.router, prefix="/api")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "vocabloom-api",
        "environment": os.getenv("ENVIRONMENT", "local")
    }

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Vocabloom API is running!"}
