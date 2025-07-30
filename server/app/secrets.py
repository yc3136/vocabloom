import os
from google.cloud import secretmanager

def get_secret(secret_name: str, default: str = None) -> str:
    """
    Get a secret from Google Cloud Secret Manager.
    
    Args:
        secret_name: Name of the secret in Secret Manager
        default: Default value if secret is not found
    
    Returns:
        The secret value or default
    """
    try:
        # Always use Secret Manager for both local and production
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "vocabloom-467020")
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"Warning: Could not load secret '{secret_name}' from Secret Manager: {e}")
        # Return default if Secret Manager fails
        return default

def get_gemini_api_key() -> str:
    """Get the Gemini API key from Secret Manager or environment."""
    return get_secret("gemini-api-key", "your_gemini_api_key_here")

def get_firebase_admin_key() -> str:
    """Get the Firebase admin key from Secret Manager or environment."""
    return get_secret("firebase-admin-key", None) 