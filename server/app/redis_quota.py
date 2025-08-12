import redis
import os
from datetime import date
from typing import Dict, Any, Optional

# Initialize Redis connection with error handling
try:
    redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=int(os.getenv('REDIS_DB', 0)),
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True
    )
    # Test connection
    redis_client.ping()
    print("Redis connection successful")
except Exception as e:
    print(f"Redis connection failed: {e}")
    # Fallback to a mock Redis client that always allows requests
    class MockRedis:
        def get(self, key):
            return "0"
        def incr(self, key):
            return 1
        def expire(self, key, time):
            pass
        def pipeline(self):
            class MockPipeline:
                def __enter__(self):
                    return self
                def __exit__(self, *args):
                    pass
                def incr(self, key):
                    return self
                def expire(self, key, time):
                    return self
                def execute(self):
                    return [1]
            return MockPipeline()
    
    redis_client = MockRedis()

# Quota limits configuration
QUOTA_LIMITS = {
    'image': 2,  # 2 images per day for signed-in users
    'story': -1,  # -1 means unlimited
    'translation': -1,  # -1 means unlimited
}

def get_quota_key(user_id: str, content_type: str, quota_date: date = None) -> str:
    """Generate Redis key for quota tracking"""
    if quota_date is None:
        quota_date = date.today()
    return f"quota:{user_id}:{content_type}:{quota_date.isoformat()}"

def check_and_increment_quota(user_id: str, content_type: str) -> bool:
    """Check quota and increment if allowed. Returns True if allowed, False if quota exceeded."""
    if content_type not in QUOTA_LIMITS:
        return True  # Unknown content type, allow
    
    limit = QUOTA_LIMITS[content_type]
    if limit == -1:
        return True  # Unlimited
    
    key = get_quota_key(user_id, content_type)
    
    try:
        # Use pipeline for atomic operation
        with redis_client.pipeline() as pipe:
            # Increment the counter
            pipe.incr(key)
            # Set expiration to 24 hours if this is the first increment
            pipe.expire(key, 86400)  # 24 hours in seconds
            results = pipe.execute()
        
        current_count = results[0]
        return current_count <= limit
        
    except Exception as e:
        print(f"Error checking quota: {e}")
        # In case of error, allow the request (fail open)
        return True

def get_remaining_quota(user_id: str, content_type: str) -> Dict[str, Any]:
    """Get remaining quota information for a user"""
    if content_type not in QUOTA_LIMITS:
        return {"limit": -1, "used": 0, "remaining": -1}
    
    limit = QUOTA_LIMITS[content_type]
    if limit == -1:
        return {"limit": -1, "used": 0, "remaining": -1}
    
    key = get_quota_key(user_id, content_type)
    
    try:
        used = int(redis_client.get(key) or 0)
        remaining = max(0, limit - used)
        
        return {
            "limit": limit,
            "used": used,
            "remaining": remaining
        }
    except Exception as e:
        print(f"Error getting quota: {e}")
        return {
            "limit": limit,
            "used": 0,
            "remaining": limit
        }

def get_user_quotas(user_id: str) -> Dict[str, Dict[str, Any]]:
    """Get quota information for all content types for a user"""
    quotas = {}
    
    for content_type in ['image', 'story', 'translation']:
        quotas[content_type] = get_remaining_quota(user_id, content_type)
    
    return quotas

def reset_user_quota(user_id: str, content_type: str) -> bool:
    """Reset quota for a specific user and content type (for testing)"""
    try:
        key = get_quota_key(user_id, content_type)
        redis_client.delete(key)
        return True
    except Exception as e:
        print(f"Error resetting quota: {e}")
        return False 