import os
import base64
from typing import Optional
from google.cloud import storage
from google.cloud.exceptions import NotFound
from google.auth import default
from google.auth.exceptions import DefaultCredentialsError


class CloudStorageManager:
    def __init__(self):
        self._client = None
        self._bucket = None
        self.bucket_name = os.getenv("GCS_BUCKET_NAME", "vocabloom-images-local")
        # Use environment-specific folders
        self.environment = os.getenv("ENVIRONMENT", "local")
        self.base_path = f"{self.environment}/images"
        self._credentials = None
    
    def _setup_credentials(self):
        """Set up Google Cloud credentials"""
        try:
            # Try to get default credentials
            self._credentials, project = default()
            print(f"✅ Using Google Cloud credentials for project: {project}")
            return True
        except DefaultCredentialsError:
            print("⚠️  Google Cloud credentials not found. Setting up local development mode...")
            # For local development, we can use a mock client or skip GCS
            return False
    
    @property
    def client(self):
        if self._client is None:
            if self._setup_credentials():
                self._client = storage.Client(credentials=self._credentials)
            else:
                # Create a mock client for local development
                self._client = self._create_mock_client()
        return self._client
    
    def _create_mock_client(self):
        """Create a mock client for local development without GCS"""
        class MockStorageClient:
            def bucket(self, bucket_name):
                return MockBucket(bucket_name)
        
        class MockBucket:
            def __init__(self, name):
                self.name = name
            
            def blob(self, path):
                return MockBlob(path)
        
        class MockBlob:
            def __init__(self, path):
                self.path = path
                self.public_url = f"https://mock-gcs.com/{path}"
            
            def upload_from_string(self, data, content_type=None):
                print(f"📁 [MOCK] Uploaded to GCS: {self.path}")
                return True
            
            def make_public(self):
                print(f"🌐 [MOCK] Made public: {self.path}")
                return True
            
            def delete(self):
                print(f"🗑️  [MOCK] Deleted from GCS: {self.path}")
                return True
            
            def exists(self):
                return True
        
        print("🔧 Using mock GCS client for local development")
        return MockStorageClient()
    
    @property
    def bucket(self):
        if self._bucket is None:
            self._bucket = self.client.bucket(self.bucket_name)
        return self._bucket
    
    def upload_image_from_base64(self, image_data: str, filename: str, content_type: str = "image/png") -> str:
        """
        Upload an image from base64 data to Google Cloud Storage
        
        Args:
            image_data: Base64 encoded image data (without data:image/... prefix)
            filename: Name for the file in GCS
            content_type: MIME type of the image
            
        Returns:
            Public URL of the uploaded image
        """
        try:
            # Decode base64 data
            if image_data.startswith('data:'):
                # Remove data URL prefix
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            
            # Create blob with environment-specific path
            blob = self.bucket.blob(f"{self.base_path}/{filename}")
            
            # Upload the image with proper content type
            blob.upload_from_string(image_bytes, content_type=content_type)
            
            # Make the blob publicly readable
            blob.make_public()
            
            return blob.public_url
            
        except Exception as e:
            print(f"Error uploading image to GCS: {e}")
            raise
    
    def upload_image_from_bytes(self, image_bytes: bytes, filename: str, content_type: str = "image/png") -> str:
        """
        Upload an image from bytes to Google Cloud Storage
        
        Args:
            image_bytes: Raw image bytes
            filename: Name for the file in GCS
            content_type: MIME type of the image
            
        Returns:
            Public URL of the uploaded image
        """
        try:
            # Create blob with environment-specific path
            blob = self.bucket.blob(f"{self.base_path}/{filename}")
            
            # Upload the image with proper content type
            blob.upload_from_string(image_bytes, content_type=content_type)
            
            # Make the blob publicly readable
            blob.make_public()
            
            return blob.public_url
            
        except Exception as e:
            print(f"Error uploading image to GCS: {e}")
            raise
    
    def delete_image(self, filename: str) -> bool:
        """
        Delete an image from Google Cloud Storage
        
        Args:
            filename: Name of the file in GCS
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            blob = self.bucket.blob(f"{self.base_path}/{filename}")
            blob.delete()
            return True
        except NotFound:
            print(f"Image {filename} not found in GCS")
            return False
        except Exception as e:
            print(f"Error deleting image from GCS: {e}")
            return False
    
    def get_image_url(self, filename: str) -> Optional[str]:
        """
        Get the public URL of an image
        
        Args:
            filename: Name of the file in GCS
            
        Returns:
            Public URL if image exists, None otherwise
        """
        try:
            blob = self.bucket.blob(f"{self.base_path}/{filename}")
            if blob.exists():
                return blob.public_url
            return None
        except Exception as e:
            print(f"Error getting image URL from GCS: {e}")
            return None


# Global instance
storage_manager = CloudStorageManager() 