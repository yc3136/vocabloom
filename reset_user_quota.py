#!/usr/bin/env python3
"""
Utility script to reset quota for a specific user by email address.
Usage: python reset_user_quota.py <email> [content_type]
"""

import sys
import os
from datetime import date

# Add the server directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))

from app.database import SessionLocal
from app.crud import get_user_by_email
from app.redis_quota import reset_user_quota

def reset_quota_by_email(email: str, content_type: str = "image"):
    """Reset quota for a user by email address"""
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Get user by email
        user = get_user_by_email(db, email)
        
        if not user:
            print(f"❌ User with email '{email}' not found in database")
            return False
        
        print(f"✅ Found user: {user.email} (ID: {user.id})")
        
        # Reset quota
        success = reset_user_quota(user.id, content_type)
        
        if success:
            print(f"✅ Successfully reset {content_type} quota for user {email}")
            return True
        else:
            print(f"❌ Failed to reset {content_type} quota for user {email}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        db.close()

def main():
    if len(sys.argv) < 2:
        print("Usage: python reset_user_quota.py <email> [content_type]")
        print("Example: python reset_user_quota.py camillecaodev@gmail.com image")
        print("Content types: image, story, translation")
        sys.exit(1)
    
    email = sys.argv[1]
    content_type = sys.argv[2] if len(sys.argv) > 2 else "image"
    
    # Validate content type
    valid_types = ["image", "story", "translation"]
    if content_type not in valid_types:
        print(f"❌ Invalid content type: {content_type}")
        print(f"Valid types: {', '.join(valid_types)}")
        sys.exit(1)
    
    print(f"🔄 Resetting {content_type} quota for user: {email}")
    
    success = reset_quota_by_email(email, content_type)
    
    if success:
        print("🎉 Quota reset completed successfully!")
    else:
        print("💥 Quota reset failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 