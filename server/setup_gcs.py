#!/usr/bin/env python3
"""
Script to set up Google Cloud Storage bucket for Vocabloom
"""

import os
import sys
from google.cloud import storage
from google.cloud.exceptions import Conflict
from google.auth import default
from google.auth.exceptions import DefaultCredentialsError


def setup_gcs_bucket():
    """Create the GCS bucket if it doesn't exist"""
    bucket_name = os.getenv("GCS_BUCKET_NAME", "vocabloom-images-local")
    
    try:
        # Check credentials first
        try:
            credentials, project = default()
            print(f"✅ Using Google Cloud credentials for project: {project}")
        except DefaultCredentialsError:
            print("❌ Google Cloud credentials not found!")
            print("\n📋 To set up credentials, run one of these commands:")
            print("\n1. For local development with gcloud CLI:")
            print("   gcloud auth application-default login")
            print("   gcloud config set project YOUR_PROJECT_ID")
            print("\n2. For service account (production):")
            print("   export GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json")
            print("\n3. For local development without GCS:")
            print("   The app will use a mock client automatically")
            print("\n🔗 More info: https://cloud.google.com/docs/authentication/external/set-up-adc")
            return False
        
        client = storage.Client(credentials=credentials)
        bucket = client.bucket(bucket_name)
        
        # Check if bucket exists
        if bucket.exists():
            print(f"✅ Bucket '{bucket_name}' already exists")
            return True
        
        # Create the bucket
        bucket = client.create_bucket(bucket_name)
        print(f"✅ Created bucket '{bucket_name}'")
        
        # Make bucket publicly readable (for image URLs)
        bucket.make_public()
        print(f"✅ Made bucket '{bucket_name}' publicly readable")
        
        return True
        
    except Conflict:
        print(f"✅ Bucket '{bucket_name}' already exists")
        return True
    except Exception as e:
        print(f"❌ Error creating bucket: {e}")
        print("Make sure you have the necessary permissions and Google Cloud credentials set up")
        return False


def check_gcs_access():
    """Check if we can access GCS"""
    try:
        credentials, project = default()
        client = storage.Client(credentials=credentials)
        # Try to list buckets to test access
        list(client.list_buckets(max_results=1))
        print(f"✅ GCS access confirmed for project: {project}")
        return True
    except Exception as e:
        print(f"❌ GCS access failed: {e}")
        return False


if __name__ == "__main__":
    print("☁️  Setting up Google Cloud Storage for Vocabloom...")
    print("=" * 50)
    
    # Check if we're in local development mode
    environment = os.getenv("ENVIRONMENT", "local")
    print(f"🌍 Environment: {environment}")
    
    if environment == "local":
        print("🔧 Local development mode detected")
        print("📝 Note: If GCS is not available, the app will use a mock client")
        print()
    
    # Try to set up the bucket
    success = setup_gcs_bucket()
    
    if success:
        print("\n🎉 GCS setup completed successfully!")
        print(f"📦 Bucket: {os.getenv('GCS_BUCKET_NAME', 'vocabloom-images-local')}")
        print(f"📁 Path: {environment}/images/")
    else:
        print("\n⚠️  GCS setup incomplete, but the app will continue with mock client")
        print("💡 You can set up GCS later and restart the app")
    
    print("\n" + "=" * 50) 