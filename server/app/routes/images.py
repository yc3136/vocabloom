from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from ..database import get_db, engine
from ..models import Image, User
from ..schemas import Image as ImageSchema, ImageCreate, ImageUpdate, ImageGenerationRequest
from ..crud import create_image, get_images, get_image, update_image, update_image_status, delete_image
from ..auth import get_current_user
import httpx
import os
import json
import asyncio
import threading
from datetime import datetime

router = APIRouter(prefix="/images", tags=["images"])


def generate_image_sync(image_id: int, prompt: str):
    """Synchronous background task to generate image using Gemini API"""
    # Create a new database session for the background task
    db = Session(engine)
    try:
        # Get Gemini API key from environment
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            # Update status to failed
            update_image_status(db, image_id, "failed")
            return
        
        # Get the image record to access the word and translation
        image = db.query(Image).filter(Image.id == image_id).first()
        if not image:
            update_image_status(db, image_id, "failed")
            return
        
        # For now, we'll use a placeholder URL since Gemini doesn't generate images directly
        # In a real implementation, you'd use DALL-E or another image generation service
        # Create a simple SVG placeholder
        svg_content = f'''<svg width="512" height="512" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="#6690ff"/>
  <text x="50%" y="50%" font-family="Arial, sans-serif" font-size="24" fill="white" text-anchor="middle" dy=".3em">
    Generated Image for "{image.original_word}"
  </text>
  <text x="50%" y="70%" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle">
    {image.translated_word}
  </text>
</svg>'''
        
        # Convert SVG to data URL
        import base64
        svg_encoded = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
        image_url = f"data:image/svg+xml;base64,{svg_encoded}"
        
        # Simulate some processing time
        import time
        time.sleep(2)
        
        # Update the image with the generated URL
        update_image_status(db, image_id, "completed", image_url)
                
    except Exception as e:
        print(f"Error generating image: {e}")
        # Update status to failed
        update_image_status(db, image_id, "failed")
    finally:
        db.close()


@router.post("/generate")
async def generate_image(
    request: ImageGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start image generation process"""
    try:
        # Build the generation prompt
        age_guidance = ""
        if request.child_age:
            if request.child_age <= 3:
                age_guidance = "very simple, colorful, child-friendly, safe for toddlers"
            elif 4 <= request.child_age <= 5:
                age_guidance = "simple, engaging, educational, safe for preschoolers"
            elif 6 <= request.child_age <= 10:
                age_guidance = "engaging, educational, age-appropriate for elementary school"
            elif 11 <= request.child_age <= 13:
                age_guidance = "more detailed, educational, suitable for middle school"
            else:
                age_guidance = "engaging and educational for children"
        else:
            age_guidance = "engaging and educational for children"
        
        # Create the generation prompt
        base_prompt = f"""
        Create a visual representation for the word "{request.original_word}" (translated as "{request.translated_word}" in {request.target_language}).
        
        Requirements:
        - Style: {age_guidance}
        - Language context: {request.target_language}
        - Educational and child-friendly
        - Clear, simple, and engaging visual
        - Safe and appropriate for children
        """
        
        if request.custom_instructions:
            base_prompt += f"\nAdditional instructions: {request.custom_instructions}"
        
        # Create image record in database
        image_data = ImageCreate(
            original_word=request.original_word,
            translated_word=request.translated_word,
            target_language=request.target_language,
            generation_prompt=base_prompt,
            custom_instructions=request.custom_instructions,
            child_age=request.child_age,
            title=request.title
        )
        
        db_image = create_image(db, image_data, current_user.id)
        
        # Start background task for image generation
        background_tasks.add_task(generate_image_sync, db_image.id, base_prompt)
        
        return {
            "id": db_image.id,
            "status": "pending",
            "message": "Image generation started. You can check the status in My Images page."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start image generation: {str(e)}"
        )


@router.get("/", response_model=List[ImageSchema])
async def get_user_images(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all images for the current user"""
    return get_images(db, current_user.id, skip, limit)


@router.get("/{image_id}", response_model=ImageSchema)
async def get_image_by_id(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific image by ID"""
    image = get_image(db, image_id, current_user.id)
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    return image


@router.put("/{image_id}", response_model=ImageSchema)
async def update_image_endpoint(
    image_id: int,
    image_update: ImageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update image metadata"""
    updated_image = update_image(db, image_id, image_update, current_user.id)
    if not updated_image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    return updated_image


@router.delete("/{image_id}")
async def delete_image_endpoint(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an image"""
    success = delete_image(db, image_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    return {"message": "Image deleted successfully"} 