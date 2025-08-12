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
        
        # Initialize Vertex AI
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "vocabloom-467020")
        location = "us-central1"
        
        vertexai.init(project=project_id, location=location)
        
        print(f"Generating image with Imagen for: {image.original_word} -> {image.translated_word}")
        
        # Load the ImageGenerationModel for Imagen 4 Standard
        model = ImageGenerationModel.from_pretrained("imagen-4.0-generate-preview-06-06")
        
        # Generate images from the text prompt
        images = model.generate_images(
            prompt=prompt,
            number_of_images=1,
            aspect_ratio="1:1",  # Square aspect ratio for consistent cards
            safety_filter_level="block_some",  # Moderate safety filtering
            person_generation="dont_allow"  # Don't generate people for safety
        )
        
        print(f"Successfully generated {len(images.images)} image(s).")
        
        if images.images:
            # Get the first generated image
            generated_image = images.images[0]
            
            # Get the image bytes directly
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
                
                # Update the image with the GCS URL
                update_image_status(db, image_id, "completed", image_url)
                return
            except Exception as e:
                print(f"Error uploading to GCS: {e}")
                # Fallback to placeholder image
                create_custom_svg_image(db, image_id, image, prompt)
                return
        else:
            print("No images generated")
            # Fallback to placeholder image
            create_custom_svg_image(db, image_id, image, prompt)
            return
                
    except Exception as e:
        print(f"Error generating image with Imagen: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to placeholder image
        try:
            image = db.query(ImageModel).filter(ImageModel.id == image_id).first()
            if image:
                create_custom_svg_image(db, image_id, image, prompt)
            else:
                update_image_status(db, image_id, "failed")
        except Exception as fallback_error:
            print(f"Fallback also failed: {fallback_error}")
            update_image_status(db, image_id, "failed")
    finally:
        db.close()


def create_custom_svg_image(db: Session, image_id: int, image: ImageModel, prompt: str):
    """Create a custom SVG image based on the prompt and word"""
    # Create a more engaging SVG with colors and styling
    svg_content = f'''<svg width="512" height="512" xmlns="http://www.w3.org/2000/svg">
<!-- Background gradient -->
<defs>
<linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
<stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
<stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
</linearGradient>
</defs>

<!-- Background -->
<rect width="100%" height="100%" fill="url(#bg)"/>

<!-- Decorative circles -->
<circle cx="100" cy="100" r="30" fill="rgba(255,255,255,0.1)"/>
<circle cx="412" cy="412" r="40" fill="rgba(255,255,255,0.1)"/>
<circle cx="412" cy="100" r="25" fill="rgba(255,255,255,0.1)"/>
<circle cx="100" cy="412" r="35" fill="rgba(255,255,255,0.1)"/>

<!-- Main content -->
<g transform="translate(256, 200)">
<!-- Original word -->
<text x="0" y="0" font-family="Arial, sans-serif" font-size="32" font-weight="bold" fill="white" text-anchor="middle">
{image.original_word}
</text>

<!-- Arrow -->
<text x="0" y="40" font-family="Arial, sans-serif" font-size="24" fill="rgba(255,255,255,0.8)" text-anchor="middle">
↓
</text>

<!-- Translation -->
<text x="0" y="80" font-family="Arial, sans-serif" font-size="28" fill="white" text-anchor="middle">
{image.translated_word}
</text>

<!-- Language -->
<text x="0" y="120" font-family="Arial, sans-serif" font-size="16" fill="rgba(255,255,255,0.7)" text-anchor="middle">
{image.target_language}
</text>
</g>

<!-- Bottom decoration -->
<rect x="50" y="450" width="412" height="2" fill="rgba(255,255,255,0.3)"/>
<text x="256" y="480" font-family="Arial, sans-serif" font-size="12" fill="rgba(255,255,255,0.6)" text-anchor="middle">
Vocabloom Learning Card
</text>
</svg>'''

    # Convert SVG to base64
    svg_encoded = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')

    # Generate filename
    filename = f"custom_svg_{image_id}_{int(time.time())}.svg"

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
        print(f"Error uploading custom SVG to GCS: {e}")
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
        Generate a colorful, engaging illustration of "{request.original_word}" (which means "{request.translated_word}" in {request.target_language}), and also write a short, educational caption describing the image.
        
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