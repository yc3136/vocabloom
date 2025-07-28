import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
import os
from google.cloud import secretmanager

# Initialize Firebase Admin SDK
def initialize_firebase():
    try:
        # Try to get Firebase credentials from Secret Manager
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/vocabloom-467020/secrets/firebase-admin-key/versions/latest"
        response = client.access_secret_version(request={"name": name})
        cred = credentials.Certificate(response.payload.data.decode("UTF-8"))
        firebase_admin.initialize_app(cred)
    except Exception as e:
        # Fallback to local development
        print(f"Warning: Could not load Firebase credentials from Secret Manager: {e}")
        print("Using default Firebase app for local development")
        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app()

# Security scheme for JWT tokens
security = HTTPBearer()

# Dependency to get current user from Firebase token
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    try:
        # Verify Firebase token
        decoded_token = auth.verify_id_token(credentials.credentials)
        user_id = decoded_token['uid']
        
        # Get or create user in database
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            # Create new user from Firebase data
            user = User(
                id=user_id,
                email=decoded_token.get('email', ''),
                display_name=decoded_token.get('name', '')
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Optional dependency for endpoints that work with or without authentication
async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User | None:
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None 