import os
import time
import base64
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
from app.redis_quota import check_and_increment_quota, get_remaining_quota

router = APIRouter(prefix="/images", tags=["images"])


def generate_image_sync(image_id: int, prompt: str):
    """Synchronous background task to generate image using Imagen API"""
    # Create a new database session for the background task
    db = Session(engine)
    try:
        # Get the image record to access the word and translation
        image = db.query(ImageModel).filter(ImageModel.id == image_id).first()
        if not image:
            print(f"Image record not found for ID: {image_id}")
            update_image_status(db, image_id, "failed")
            return
        
        # Import Vertex AI
        import vertexai
        from vertexai.preview.vision_models import ImageGenerationModel
        
        # Initialize Vertex AI with fresh connection
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "vocabloom-467020")
        location = "us-central1"
        
        # Reset and reinitialize Vertex AI to ensure clean state
        try:
            vertexai.init(project=project_id, location=location)
            print(f"Vertex AI initialized for project: {project_id}")
        except Exception as init_error:
            print(f"Vertex AI init error: {init_error}")
            update_image_status(db, image_id, "failed")
            return
        
        print(f"Generating image with Imagen for: {image.original_word} -> {image.translated_word}")
        
        # Load the ImageGenerationModel for Imagen
        model = ImageGenerationModel.from_pretrained("imagen-4.0-generate-preview-06-06")
        
        # Generate images from the text prompt
        print(f"Calling Imagen API with prompt: {prompt[:100]}...")
        images = model.generate_images(
            prompt=prompt,
            number_of_images=1
        )
        print(f"API call completed successfully")
        
        print(f"Successfully generated {len(images.images)} image(s).")
        
        if images.images:
            # Get the first generated image
            generated_image = images.images[0]
            
            # Check if there's any generated title or description (simple field access only)
            generated_title = None
            if hasattr(generated_image, 'caption') and generated_image.caption:
                generated_title = generated_image.caption
            elif hasattr(generated_image, 'description') and generated_image.description:
                generated_title = generated_image.description
            
            # Get the image bytes directly (working approach)
            img_byte_arr = generated_image._image_bytes
            
            # Generate filename
            filename = f"imagen_{image_id}_{int(time.time())}.png"
            
            # Upload to Google Cloud Storage
            try:
                image_url = storage_manager.upload_image_from_bytes(
                    img_byte_arr,
                    filename,
                    "image/png"
                )
                
                print(f"Image uploaded successfully: {image_url}")
                
                # Update the image with the GCS URL and any generated title
                if generated_title:
                    print(f"Generated title: {generated_title}")
                    update_image_status(db, image_id, "completed", image_url, generated_title)
                else:
                    update_image_status(db, image_id, "completed", image_url)
                return
            except Exception as e:
                print(f"Error uploading to GCS: {e}")
                update_image_status(db, image_id, "failed")
                return
        else:
            print("No images generated")
            update_image_status(db, image_id, "failed")
            return
                
    except Exception as e:
        print(f"Error generating image with Imagen: {e}")
        import traceback
        traceback.print_exc()
        # Mark as failed
        update_image_status(db, image_id, "failed")
    finally:
        db.close()





def update_image_status(db: Session, image_id: int, status: str, image_url: str = None, title: str = None):
    """Update image status and optionally the image URL and title"""
    try:
        image = db.query(ImageModel).filter(ImageModel.id == image_id).first()
        if image:
            image.status = status
            if image_url:
                image.image_url = image_url
            if title:
                image.title = title
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
        # Check quota before starting generation
        if not check_and_increment_quota(current_user.id, 'image'):
            quota_info = get_remaining_quota(current_user.id, 'image')
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Daily image generation limit reached. You have used {quota_info['used']}/{quota_info['limit']} images today. Please try again tomorrow."
            )
        # Build the generation prompt
        age_guidance = ""
        if request.child_age:
            if request.child_age <= 3:
                age_guidance = "very simple, colorful, child-friendly, safe for toddlers, large simple objects, basic shapes"
            elif 4 <= request.child_age <= 5:
                age_guidance = "simple, engaging, educational, safe for preschoolers, clear objects, bright colors"
            elif 6 <= request.child_age <= 10:
                age_guidance = "engaging, educational, age-appropriate for elementary school, detailed but clear, colorful"
            elif 11 <= request.child_age <= 13:
                age_guidance = "more detailed, educational, suitable for middle school, sophisticated but still colorful and clear"
            else:
                age_guidance = "engaging and educational for children, colorful and clear"
        else:
            age_guidance = "engaging and educational for children, colorful and clear"
        
        # Create the generation prompt
        base_prompt = f"""
        Create a simple, colorful educational illustration for children learning {request.target_language}.

        CRITICAL REQUIREMENTS:
        - DO NOT include any text, words, letters, or writing in the image
        - DO NOT include any labels, captions, or text overlays
        - DO NOT include any metadata, instructions, or technical information
        - The image should be completely text-free
        - Show ONLY a visual illustration of "{request.original_word}" (which means "{request.translated_word}" in {request.target_language})
        - Use bright, child-friendly colors
        - Simple cartoon style with clean lines
        - White background
        - Focus only on the visual representation of the word/concept
        - Fill the entire canvas with the illustration
        - Use the full available space effectively
        - Make the illustration large and prominent

        Style: Simple, educational, colorful, child-friendly, clean design, full canvas utilization, ABSOLUTELY NO TEXT
        """
        
        # Add simple word type guidance
        original_word_lower = request.original_word.lower()
        
        if any(word in original_word_lower for word in ['run', 'jump', 'walk', 'eat', 'sleep', 'play', 'dance', 'sing', 'read', 'write']):
            base_prompt += "\nShow the action being performed visually (no text)."
        elif any(word in original_word_lower for word in ['big', 'small', 'tall', 'short', 'fast', 'slow', 'hot', 'cold', 'happy', 'sad']):
            base_prompt += "\nShow contrasting examples to illustrate the concept visually (no text)."
        elif any(word in original_word_lower for word in ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'brown', 'black', 'white']):
            base_prompt += "\nShow the color prominently (no text labels)."
        else:
            base_prompt += "\nShow the object/concept clearly (no text)."
        
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
        
    except HTTPException:
        # Re-raise HTTP exceptions (like quota limits) without modification
        raise
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