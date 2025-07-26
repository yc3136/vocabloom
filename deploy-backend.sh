#!/bin/bash

# Vocabloom Backend Deployment Script

set -e

echo "🚀 Deploying Vocabloom Backend..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -d "server" ]; then
    print_error "Please run this script from the vocabloom root directory"
    exit 1
fi

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI is not installed"
    exit 1
fi

# Deploy backend
print_status "Deploying backend to Cloud Run..."

cd server

# Check if Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    print_error "Dockerfile not found in server directory"
    exit 1
fi

# Deploy to Cloud Run
print_status "Building and deploying backend..."
gcloud run deploy vocabloom-api \
    --source . \
    --region=us-central1 \
    --allow-unauthenticated \
    --platform=managed \
    --quiet

print_success "Backend deployed successfully!"

# Test the deployment
print_status "Testing backend deployment..."
BACKEND_URL=$(gcloud run services describe vocabloom-api --region=us-central1 --format="value(status.url)")

if curl -f "$BACKEND_URL/health" > /dev/null 2>&1; then
    print_success "Backend health check passed"
else
    print_error "Backend health check failed"
fi

cd ..

print_success "🎉 Backend deployment complete!" 