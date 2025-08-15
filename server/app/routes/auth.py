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
            password=user_data.password
        )
        
        # Create user in database
        db_user = create_user(db, UserRegistration(
            id=firebase_user.uid,
            email=user_data.email
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
    # Update last login time when user profile is accessed
    updated_user = update_user_last_login(db, current_user.id)
    return updated_user


@router.post("/google", response_model=UserSchema)
async def handle_google_auth(
    user_data: dict,
    db: Session = Depends(get_db)
):
    """Handle Google authentication - create user if doesn't exist"""
    try:
        # Check if user already exists
        existing_user = get_user_by_email(db, user_data.get("email"))
        
        if existing_user:
            # User exists, update last login and return
            updated_user = update_user_last_login(db, existing_user.id)
            return updated_user
        else:
            # Create new user in database
            db_user = create_user(db, UserRegistration(
                id=user_data.get("uid"),
                email=user_data.get("email")
            ))
            return db_user
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google authentication failed: {str(e)}"
        )


@router.get("/preferences", response_model=UserPreferences)
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user preferences"""
    user_prefs = current_user.preferences or {}
    return {
        "child_name": user_prefs.get("child_name"),
        "child_age": user_prefs.get("child_age"),
        "preferred_languages": user_prefs.get("preferred_languages", []) or [],
        "content_privacy_default": user_prefs.get("content_privacy_default", "private") or "private"
    }


@router.put("/preferences", response_model=UserSchema)
async def update_user_preferences_endpoint(
    preferences_update: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user preferences"""
    try:
        # Update user in database
        preferences_dict = None
        if preferences_update.preferences:
            preferences_dict = preferences_update.preferences.dict(exclude_none=True)
        
        updated_user = update_user_preferences(
            db=db,
            user_id=current_user.id,
            preferences=preferences_dict
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