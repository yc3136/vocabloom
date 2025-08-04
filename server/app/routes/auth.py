from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import UserRegistration, UserLogin, User as UserSchema, UserPreferencesUpdate, UserDelete, UserPreferences
from ..auth import get_current_user
from ..crud import create_user, get_user_by_email, update_user_last_login, update_user_preferences, delete_user_account
import firebase_admin
from firebase_admin import auth

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserSchema)
async def register_user(
    user_data: UserRegistration,
    db: Session = Depends(get_db)
):
    """Register a new user with Firebase Auth"""
    try:
        # Check if user already exists
        existing_user = get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create user in Firebase Auth
        firebase_user = auth.create_user(
            email=user_data.email,
            password=user_data.password,
            display_name=user_data.display_name
        )
        
        # Create user in database
        db_user = create_user(db, UserRegistration(
            id=firebase_user.uid,
            email=user_data.email,
            display_name=user_data.display_name
        ))
        
        return db_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    print(f"[AUTH ME] Endpoint called")
    print(f"[AUTH ME] Current user: {current_user.id}, email: {current_user.email}")
    try:
        print(f"[AUTH ME] About to return user data")
        return current_user
    except Exception as e:
        print(f"[AUTH ME] Exception in endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise


@router.get("/preferences", response_model=UserPreferences)
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user preferences"""
    return current_user.preferences or {}


@router.put("/preferences", response_model=UserSchema)
async def update_user_preferences(
    preferences_update: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user preferences"""
    try:
        # Update display name in Firebase if provided
        if preferences_update.display_name:
            auth.update_user(
                current_user.id,
                display_name=preferences_update.display_name
            )
        
        # Update user in database
        updated_user = update_user_preferences(
            db=db,
            user_id=current_user.id,
            display_name=preferences_update.display_name,
            preferences=preferences_update.preferences.dict() if preferences_update.preferences else None
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return updated_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update preferences: {str(e)}"
        )


@router.delete("/account")
async def delete_user_account_endpoint(
    delete_data: UserDelete,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user account and all associated data"""
    # Verify email confirmation
    if delete_data.confirm_email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email confirmation does not match"
        )
    
    try:
        # Delete user from Firebase Auth
        auth.delete_user(current_user.id)
        
        # Delete user from database (this will cascade delete all user data)
        success = delete_user_account(db, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {"message": "Account deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete account: {str(e)}"
        )