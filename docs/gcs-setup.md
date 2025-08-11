# Google Cloud Storage Setup

## Overview

Vocabloom uses Google Cloud Storage (GCS) for storing generated images. This provides:
- Scalable and reliable image storage
- Public URLs for easy access
- Cost-effective storage solution
- Automatic cleanup when images are deleted

## Environment Configuration

### Local Development
- **Bucket**: `vocabloom-images-local`
- **Path**: `local/images/`
- **Purpose**: Isolated development environment

### Production
- **Bucket**: `vocabloom-images` (or custom)
- **Path**: `production/images/`
- **Purpose**: Live application data

## Setup Instructions

### 1. Google Cloud Project Setup
```bash
# Install Google Cloud CLI
# Follow: https://cloud.google.com/sdk/docs/install

# Authenticate with your project
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 2. Create Storage Buckets
```bash
# For local development
gsutil mb gs://vocabloom-images-local

# For production
gsutil mb gs://vocabloom-images

# Make buckets publicly readable (for image URLs)
gsutil iam ch allUsers:objectViewer gs://vocabloom-images-local
gsutil iam ch allUsers:objectViewer gs://vocabloom-images
```

### 3. Environment Variables
Add to your `.env` file:
```bash
# Local development
GCS_BUCKET_NAME=vocabloom-images-local
ENVIRONMENT=local

# Production
GCS_BUCKET_NAME=vocabloom-images
ENVIRONMENT=production
```

### 4. Service Account (Production)
For production deployment, create a service account:
```bash
# Create service account
gcloud iam service-accounts create vocabloom-storage \
    --display-name="Vocabloom Storage Service Account"

# Grant storage permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:vocabloom-storage@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

# Download key file
gcloud iam service-accounts keys create gcs-key.json \
    --iam-account=vocabloom-storage@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

## Best Practices

### 1. Environment Separation
- Use different buckets for local and production
- Prevents accidental data mixing
- Easier cost tracking and management

### 2. Security
- Buckets are publicly readable for image URLs
- Service accounts used for write operations
- No sensitive data stored in images

### 3. Cost Optimization
- Images are automatically deleted when records are removed
- Use appropriate storage classes for different access patterns
- Monitor usage with Cloud Monitoring

### 4. File Organization
- Environment-specific folders: `local/images/`, `production/images/`
- Unique filenames with timestamps: `image_123_1703123456.png`
- Proper content-type headers for browser compatibility

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```bash
   # Check credentials
   gcloud auth list
   gcloud config list
   ```

2. **Permission Errors**
   ```bash
   # Verify bucket permissions
   gsutil iam get gs://YOUR_BUCKET_NAME
   ```

3. **Bucket Not Found**
   ```bash
   # List buckets
   gsutil ls
   # Create if missing
   gsutil mb gs://YOUR_BUCKET_NAME
   ```

### Local Development
The `run_vocabloom.sh` script automatically runs GCS setup:
```bash
./run_vocabloom.sh
```

This will:
- Check if the bucket exists
- Create it if missing
- Make it publicly readable
- Set up proper permissions 