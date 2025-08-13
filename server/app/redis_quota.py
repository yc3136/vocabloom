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
    'image': 10,  # 10 images per day for signed-in users
    'story': -1,  # -1 means unlimited
    'translation': -1,  # -1 means unlimited
}

def get_quota_key(user_id: str, content_type: str, quota_date: date = None) -> str:
    """Generate Redis key for quota tracking"""
    if quota_date is None:
        quota_date = date.today()
    return f"quota:{user_id}:{content_type}:{quota_date.isoformat()}"

def check_quota_only(user_id: str, content_type: str) -> bool:
    """Check quota without incrementing. Returns True if allowed, False if quota exceeded."""
    if content_type not in QUOTA_LIMITS:
        return True  # Unknown content type, allow
    
    limit = QUOTA_LIMITS[content_type]
    if limit == -1:
        return True  # Unlimited
    
    key = get_quota_key(user_id, content_type)
    
    try:
        current_count = int(redis_client.get(key) or 0)
        return current_count < limit
        
    except Exception as e:
        print(f"Error checking quota: {e}")
        # In case of error, allow the request (fail open)
        return True

def check_and_increment_quota(user_id: str, content_type: str) -> bool:
    """Check quota and increment if allowed. Returns True if allowed, False if quota exceeded."""
    if content_type not in QUOTA_LIMITS:
        return True  # Unknown content type, allow
    
    limit = QUOTA_LIMITS[content_type]
    if limit == -1:
        return True  # Unlimited
    
    key = get_quota_key(user_id, content_type)
    
    try:
        # Use Lua script for atomic check-and-increment operation
        lua_script = """
        local current = redis.call('get', KEYS[1]) or 0
        local limit = tonumber(ARGV[1])
        local current_num = tonumber(current)
        
        if current_num < limit then
            redis.call('incr', KEYS[1])
            redis.call('expire', KEYS[1], ARGV[2])
            return 1
        else
            return 0
        end
        """
        
        result = redis_client.eval(lua_script, 1, key, limit, 86400)
        return bool(result)
        
    except Exception as e:
        print(f"Error checking quota: {e}")
        # In case of error, allow the request (fail open)
        return True

def decrement_quota(user_id: str, content_type: str) -> bool:
    """Decrement quota for a user (useful for failed operations). Returns True if successful."""
    if content_type not in QUOTA_LIMITS:
        return True  # Unknown content type
    
    limit = QUOTA_LIMITS[content_type]
    if limit == -1:
        return True  # Unlimited
    
    key = get_quota_key(user_id, content_type)
    
    try:
        # Use pipeline for atomic operation
        with redis_client.pipeline() as pipe:
            # Decrement the counter, but don't go below 0
            pipe.eval("""
                local current = redis.call('get', KEYS[1]) or 0
                if tonumber(current) > 0 then
                    redis.call('decr', KEYS[1])
                end
                return redis.call('get', KEYS[1]) or 0
            """, 1, key)
            results = pipe.execute()
        
        return True
        
    except Exception as e:
        print(f"Error decrementing quota: {e}")
        return False

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

def get_pending_generations_key(user_id: str, content_type: str) -> str:
    """Generate Redis key for tracking pending generations"""
    return f"pending:{user_id}:{content_type}"

def has_pending_generation(user_id: str, content_type: str) -> bool:
    """Check if user has any pending generations"""
    try:
        key = get_pending_generations_key(user_id, content_type)
        return bool(redis_client.get(key))
    except Exception as e:
        print(f"Error checking pending generations: {e}")
        return False

def start_generation(user_id: str, content_type: str) -> bool:
    """Mark that a generation has started (with 5-minute timeout)"""
    try:
        key = get_pending_generations_key(user_id, content_type)
        redis_client.setex(key, 300, "1")  # 5 minutes timeout
        return True
    except Exception as e:
        print(f"Error starting generation: {e}")
        return False

def end_generation(user_id: str, content_type: str) -> bool:
    """Mark that a generation has ended"""
    try:
        key = get_pending_generations_key(user_id, content_type)
        redis_client.delete(key)
        return True
    except Exception as e:
        print(f"Error ending generation: {e}")
        return False 