import os
import time
import httpx
import asyncio
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from app.database import get_db, engine
from app.models import Image as ImageModel, User
from app.schemas import Image, ImageCreate, ImageUpdate, ImageGenerationRequest
from app.crud import create_image, get_image, update_image, delete_image, update_image_status, get_images
from app.auth import get_current_user
from app.storage import storage_manager

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
        image = db.query(ImageModel).filter(ImageModel.id == image_id).first()
        if not image:
            update_image_status(db, image_id, "failed")
            return
        
        # Call Gemini Image Generation API
        async def generate_with_gemini():
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-preview-image-generation:generateContent?key={gemini_api_key}",
                    json={
                        "contents": [{
                            "parts": [{
                                "text": prompt
                            }]
                        }],
                        "generationConfig": {
                            "temperature": 0.7,
                            "topK": 40,
                            "topP": 0.95,
                            "maxOutputTokens": 1024,
                        },
                        "responseMimeType": "image/png"
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Extract image data from response
                    if "candidates" in data and len(data["candidates"]) > 0:
                        candidate = data["candidates"][0]
                        if "content" in candidate and "parts" in candidate["content"]:
                            for part in candidate["content"]["parts"]:
                                if "inlineData" in part:
                                    # This is the generated image data
                                    image_data = part["inlineData"]["data"]
                                    mime_type = part["inlineData"]["mimeType"]
                                    
                                    # Generate filename
                                    filename = f"image_{image_id}_{int(time.time())}.{mime_type.split('/')[-1]}"
                                    
                                    # Upload to Google Cloud Storage
                                    try:
                                        image_url = storage_manager.upload_image_from_base64(
                                            image_data, 
                                            filename, 
                                            mime_type
                                        )
                                        
                                        # Update the image with the GCS URL
                                        update_image_status(db, image_id, "completed", image_url)
                                        return
                                    except Exception as e:
                                        print(f"Error uploading to GCS: {e}")
                                        # Fall back to placeholder
                                        create_placeholder_image(db, image_id, image)
                                        return
                    
                    # If no image data found, fall back to placeholder
                    print("No image data found in Gemini response, using placeholder")
                    create_placeholder_image(db, image_id, image)
                else:
                    print(f"Gemini API error: {response.status_code} - {response.text}")
                    # Fall back to placeholder on API error
                    create_placeholder_image(db, image_id, image)
        
        # Run the async function in a sync context
        try:
            asyncio.run(generate_with_gemini())
        except Exception as e:
            print(f"Error in async generation: {e}")
            # Fall back to placeholder
            create_placeholder_image(db, image_id, image)
                
    except Exception as e:
        print(f"Error generating image: {e}")
        # Update status to failed
        update_image_status(db, image_id, "failed")
    finally:
        db.close()


def create_placeholder_image(db: Session, image_id: int, image: ImageModel):
    """Create a placeholder SVG image and upload to GCS"""
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
    
    # Convert SVG to base64
    import base64
    svg_encoded = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
    
    # Generate filename
    filename = f"placeholder_{image_id}_{int(time.time())}.svg"
    
    try:
        # Upload to Google Cloud Storage
        image_url = storage_manager.upload_image_from_base64(
            svg_encoded, 
            filename, 
            "image/svg+xml"
        )
        
        # Update the image with the GCS URL
        update_image_status(db, image_id, "completed", image_url)
    except Exception as e:
        print(f"Error uploading placeholder to GCS: {e}")
        # If GCS fails, update status to failed
        update_image_status(db, image_id, "failed")


def update_image_status(db: Session, image_id: int, status: str, image_url: str = None):
    """Update image status and optionally the image URL"""
    try:
        image = db.query(ImageModel).filter(ImageModel.id == image_id).first()
        if image:
            image.status = status
            if image_url:
                image.image_url = image_url
            image.updated_at = datetime.utcnow()
            db.commit()
    except Exception as e:
        print(f"Error updating image status: {e}")
        db.rollback()


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
        Generate a colorful, engaging illustration of "{request.original_word}" (which means "{request.translated_word}" in {request.target_language}).
        
        Style requirements:
        - {age_guidance}
        - Bright, vibrant colors
        - Simple, clear shapes and lines
        - Cartoon or illustration style
        - Centered composition
        - White or light background
        - No text or words in the image
        - Safe and appropriate for children
        
        Make it visually appealing and educational for language learning.
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


@router.get("/", response_model=List[Image])
async def get_user_images(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all images for the current user"""
    images = get_images(db, current_user.id, skip=skip, limit=limit)
    return images


@router.get("/{image_id}", response_model=Image)
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


@router.put("/{image_id}", response_model=Image)
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