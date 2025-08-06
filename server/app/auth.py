import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Firebase Admin SDK
def initialize_firebase():
    try:
        # Check if we're in local development
        environment = os.getenv("ENVIRONMENT", "local")
        
        if environment == "local":
            # For local development, try to use service account key file
            service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
            if service_account_path and os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
            else:
                # Fallback to default app without credentials
                try:
                    firebase_admin.get_app()
                except ValueError:
                    firebase_admin.initialize_app()
            return
        
        # For production, use Secret Manager for Firebase credentials
        from google.cloud import secretmanager
        import json
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/vocabloom-467020/secrets/firebase-admin-key/versions/latest"
        response = client.access_secret_version(request={"name": name})
        # Parse the JSON string into a dictionary
        service_account_info = json.loads(response.payload.data.decode("UTF-8"))
        cred = credentials.Certificate(service_account_info)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        # Fallback to default app if Secret Manager fails
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
        # Check environment
        environment = os.getenv("ENVIRONMENT", "local")
        
        # Verify Firebase token
        decoded_token = auth.verify_id_token(credentials.credentials)
        user_id = decoded_token['uid']
        
        # Get or create user in database
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            # Create new user from Firebase data
            user = User(
                id=user_id,
                email=decoded_token.get('email', '')
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Update user info if needed
            if user.email != decoded_token.get('email', ''):
                user.email = decoded_token.get('email', '')
                db.commit()
                db.refresh(user)
        
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {e}",
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

# Dependency that doesn't require Authorization header
async def get_current_user_if_authenticated(
    request: Request,
    db: Session = Depends(get_db)
) -> User | None:
    try:
        authorization = request.headers.get('authorization')
        if not authorization or not authorization.startswith('Bearer '):
            return None
            
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=authorization[7:])
        return await get_current_user(credentials, db)
    except:
        return None 